"""
IMPORTANT usage note:
place slurm_settings.areg at the same folder where script is located
modify cluster_configuration.json according to cluster configuration
and builds available
"""
import argparse
import errno
import getpass
import json
import os
import re

import requests
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
from collections import OrderedDict
from datetime import datetime

import wx
from wx.lib.wordwrap import wordwrap
import wx._core
import wx.dataview

from influxdb import InfluxDBClient

from gui.src_gui import GUIFrame

__authors__ = "Maksim Beliaev, Leon Voss"
__version__ = "v3.2.2"

STATISTICS_SERVER = "OTTBLD02"
STATISTICS_PORT = 8086

FIREFOX = "/bin/firefox"  # path to installation of firefox for Overwatch

# read cluster configuration from a file
cluster_configuration_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cluster_configuration.json")
try:
    with open(cluster_configuration_file) as config_file:
        cluster_config = json.load(config_file, object_pairs_hook=OrderedDict)
except FileNotFoundError:
    print("\nConfiguration file does not exist!\nCheck existence of " + cluster_configuration_file)
    sys.exit()
except json.decoder.JSONDecodeError:
    print(
        "\nConfiguration file is wrong!\nCheck format of {} \nOnly double quotes are allowed!".format(
            cluster_configuration_file
        )
    )
    sys.exit()


try:
    path_to_ssh = cluster_config["path_to_ssh"]
    overwatch_url = cluster_config["overwatch_url"]
    overwatch_api_url = cluster_config["overwatch_api_url"]

    # dictionary for the versions
    default_version = cluster_config["default_version"]
    install_dir = cluster_config["install_dir"]

    # define queue dependent number of cores and RAM per node (interactive mode)
    queue_config_dict = cluster_config["queue_config_dict"]

    # dictionary in which we will pop up dynamically information about the load from the OverWatch
    # this dictionary also serves to define parallel environments for each queue
    default_queue = cluster_config["default_queue"]

    project_path = cluster_config["user_project_path_root"]

    admin_env_vars = cluster_config.pop("environment_vars", None)
except KeyError as key_e:
    print(
        (
            "\nConfiguration file is wrong!\nCheck format of {} \nOnly double quotes are allowed."
            + "\nFollowing key does not exist: {}"
        ).format(cluster_configuration_file, key_e.args[0])
    )
    sys.exit()


parser = argparse.ArgumentParser()
parser.add_argument("--debug", help="Debug mode", action="store_true")
cli_args = parser.parse_args()
DEBUG_MODE = cli_args.debug

# create keys for usage statistics that would be updated later
queue_dict = {name: {} for name in queue_config_dict}
for queue_val in queue_dict.values():
    queue_val["total_cores"] = 100
    queue_val["avail_cores"] = 0
    queue_val["used_cores"] = 100
    queue_val["reserved_cores"] = 0
    queue_val["failed_cores"] = 0

# list to keep information about running jobs
qstat_list = []
log_dict = {"pid": "0", "msg": "None", "scheduler": False}


class ClearMsgPopupMenu(wx.Menu):
    def __init__(self, parent):
        super(ClearMsgPopupMenu, self).__init__()

        self.parent = parent

        mmi = wx.MenuItem(self, wx.NewId(), "Clear All Messages")
        self.Append(mmi)
        self.Bind(wx.EVT_MENU, self.on_clear, mmi)

    def on_clear(self, *args):
        self.parent.scheduler_msg_viewlist.DeleteAllItems()
        self.parent.log_data = {"Message List": [], "PID List": [], "GUI Data": []}

        if os.path.isfile(self.parent.logfile):
            os.remove(self.parent.logfile)


# create a new event to bind it and call it from subthread. UI should be changed ONLY in MAIN THREAD
# signal - cluster load
my_SIGNAL_EVT = wx.NewEventType()
SIGNAL_EVT = wx.PyEventBinder(my_SIGNAL_EVT, 1)

# signal - qstat
NEW_SIGNAL_EVT_QSTAT = wx.NewEventType()
SIGNAL_EVT_QSTAT = wx.PyEventBinder(NEW_SIGNAL_EVT_QSTAT, 1)

# signal - log message
NEW_SIGNAL_EVT_LOG = wx.NewEventType()
SIGNAL_EVT_LOG = wx.PyEventBinder(NEW_SIGNAL_EVT_LOG, 1)

# signal - status bar
NEW_SIGNAL_EVT_BAR = wx.NewEventType()
SIGNAL_EVT_BAR = wx.PyEventBinder(NEW_SIGNAL_EVT_BAR, 1)


class SignalEvent(wx.PyCommandEvent):
    """Event to signal that we are ready to update the plot"""

    def __init__(self, etype, eid):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)


class ClusterLoadUpdateThread(threading.Thread):
    def __init__(self, parent):
        """
        @param parent: The gui object that should receive the value
        """
        threading.Thread.__init__(self)
        self._parent = parent

    def run(self):
        """Overrides Thread.run.

        Don't call this directly its called internally when you call
        Thread.start().

        Gets cluster load every 60 seconds. 0.5s step is used to be
        able to stop subthread earlier by triggering parent.running
        Update a list of jobs status for a user every 5s
        """
        counter = 120
        while self._parent.running:
            if counter % 120 == 0:
                try:
                    self.parse_cluster_load()
                except (requests.exceptions.BaseHTTPError, requests.exceptions.RequestException):
                    print("Cannot reach OverWatch server")
                except KeyError:
                    print("Cannot parse OverWatch data. Probably Service is down.")

                counter = 0

            if counter % 10 == 0:
                self.parse_user_jobs()

            time.sleep(0.5)
            counter += 1

    def parse_user_jobs(self):
        qstat_list.clear()
        slurm_stat_output = subprocess.check_output(self._parent.squeue, shell=True)
        slurm_stat_output = slurm_stat_output.decode("ascii", errors="ignore")
        exclude = cluster_config["vnc_nodes"] + cluster_config["dcv_nodes"]
        for i, line in enumerate(slurm_stat_output.split("\n")[1:]):
            pid = line[0:18].strip()
            # partition = line[19:28].strip()
            job_name = line[29:38].strip()
            user = line[38:47].strip()
            state = line[48:49].strip()
            num_cpu = line[50:54].strip()
            started = line[54:75].strip()
            node_list = line[76:].strip()

            for node in exclude:
                if node in node_list:
                    break
            else:
                # it is neither VNC nor DCV job
                qstat_list.append(
                    {
                        "pid": pid,
                        "state": state,
                        "name": job_name,
                        "user": user,
                        "queue_data": node_list,
                        "proc": num_cpu,
                        "started": started,
                    }
                )
        evt = SignalEvent(NEW_SIGNAL_EVT_QSTAT, -1)
        wx.PostEvent(self._parent, evt)
        # get message texts
        for pid in self._parent.log_data["PID List"]:
            o_file = os.path.join(self._parent.user_dir, "ansysedt.o" + pid)
            if os.path.exists(o_file):
                output_text = ""
                with open(o_file, "r") as file:
                    for msgline in file:
                        output_text += msgline
                    if output_text != "":
                        log_dict["pid"] = pid
                        log_dict["msg"] = "Submit Message: " + output_text
                        log_dict["scheduler"] = True
                        evt = SignalEvent(NEW_SIGNAL_EVT_LOG, -1)
                        wx.PostEvent(self._parent, evt)
                os.remove(o_file)

            e_file = os.path.join(self._parent.user_dir, "ansysedt.e" + pid)
            if os.path.exists(e_file):
                error_text = ""
                with open(e_file, "r") as file:
                    for msgline in file:
                        error_text += msgline
                    if error_text != "":
                        log_dict["pid"] = pid
                        log_dict["msg"] = "Submit Error: " + error_text
                        log_dict["scheduler"] = True
                        evt = SignalEvent(NEW_SIGNAL_EVT_LOG, -1)
                        wx.PostEvent(self._parent, evt)

                os.remove(e_file)

    def parse_cluster_load(self):
        """Parse data from Overwatch and generates dictionary with cluster load for each queue."""

        # with requests.get(overwatch_url, params={"cluster": "ott"}) as url_req:  # could be used with params
        with requests.get(f"{overwatch_api_url}/api/v1/overwatch/minclusterstatus") as url_req:
            cluster_data = url_req.json()

        for queue_elem in cluster_data["QueueStatus"]:
            queue_name = queue_elem["name"]
            if queue_name in queue_dict:
                queue_dict[queue_name]["total_cores"] = queue_elem["totalSlots"]
                queue_dict[queue_name]["used_cores"] = queue_elem["totalUsedSlots"]
                queue_dict[queue_name]["failed_cores"] = queue_elem["totalUnavailableSlots"]
                queue_dict[queue_name]["reserved_cores"] = queue_elem["totalReservedSlots"]
                queue_dict[queue_name]["avail_cores"] = queue_elem["totalAvailableSlots"]
        evt = SignalEvent(my_SIGNAL_EVT, -1)
        wx.PostEvent(self._parent, evt)


class FlashStatusBarThread(threading.Thread):
    def __init__(self, parent):
        """
        @param parent: The gui object that should receive the value
        """
        threading.Thread.__init__(self)
        self._parent = parent

    def run(self):
        """Overrides Thread.run. Don't call this directly its called internally
        when you call Thread.start().
        alternates the color of the status bar for run_sec (6s) to take attention
        at the end clears the status message
        """

        if self._parent.bar_level == "i":
            alternating_color = wx.GREEN
        elif self._parent.bar_level == "!":
            alternating_color = wx.RED

        run_sec = 6
        for i in range(run_sec * 2):
            self._parent.bar_color = wx.WHITE if i % 2 == 0 else alternating_color

            if i == run_sec * 2 - 1:
                self._parent.bar_text = "No Status Message"
                self._parent.bar_color = wx.WHITE

            evt = SignalEvent(NEW_SIGNAL_EVT_BAR, -1)
            wx.PostEvent(self._parent, evt)

            time.sleep(0.5)


class LauncherWindow(GUIFrame):
    def __init__(self, parent):
        global default_queue
        # Initialize the main form
        GUIFrame.__init__(self, parent)
        GUIFrame.SetTitle(self, f"Ansys Electronics Desktop Launcher {__version__}")

        # Get environment data
        self.user_dir = os.path.expanduser("~")
        self.app_dir = self.ensure_app_folder()
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.display_node = os.getenv("DISPLAY")
        self.squeue = 'squeue --me --format "%.18i %.9P %.8j %.8u %.2t %.4C %.20V %R"'

        # get paths
        self.user_build_json = os.path.join(self.app_dir, "user_build.json")
        self.default_settings_json = os.path.join(self.app_dir, "default.json")

        self.builds_data = {}
        self.default_settings = {}

        # generate list of products for registry
        self.products = {}
        for key in list(install_dir.keys()):
            try:
                with open(os.path.join(install_dir[key], "config", "ProductList.txt")) as file:
                    self.products[key] = next(file).rstrip()  # get first line
            except FileNotFoundError:
                print(f"Installation is corrupted {install_dir[key]}")
                install_dir.pop(key)

        # set default project path
        self.path_textbox.Value = os.path.join(project_path, self.username)

        self.display_node = self.check_display_var()

        # check if we are on VNC or DCV node
        viz_type = None
        for node in cluster_config["vnc_nodes"]:
            if node in self.display_node:
                viz_type = "VNC"
                break
        else:
            for node in cluster_config["dcv_nodes"]:
                if node in self.display_node:
                    viz_type = "DCV"
                    break

        msg = "No Status Message"
        if viz_type is None:
            add_message(
                message=(
                    "Display Type is unknown: cannot identify VNC/DCV. "
                    "Interactive Submission might fail.\n"
                    "Contact cluster administrator."
                ),
                title="Display Type Error",
                icon="!",
            )
            msg = "Warning: Unknown Display Type!!"
            viz_type = ""

        # Set the status bars on the bottom of the window
        self.m_status_bar.SetStatusText(f"User: {self.username} on {viz_type} node {self.display_node}", 0)
        self.m_status_bar.SetStatusText(msg, 1)
        self.m_status_bar.SetStatusWidths([500, -1])

        init_combobox(install_dir.keys(), self.m_select_version1, default_version)

        # Setup Process Log
        self.scheduler_msg_viewlist.AppendTextColumn("Timestamp", width=140)
        self.scheduler_msg_viewlist.AppendTextColumn("PID", width=75)
        self.scheduler_msg_viewlist.AppendTextColumn("Message")
        self.logfile = os.path.join(self.app_dir, "user_log_" + viz_type + ".json")

        # read in previous log file
        self.log_data = {"Message List": [], "PID List": [], "GUI Data": []}
        if os.path.exists(self.logfile):
            try:
                with open(self.logfile, "r") as file:
                    self.log_data = json.load(file)
                    self.update_msg_list()
            except json.decoder.JSONDecodeError:
                print("Error reading log file")
                os.remove(self.logfile)

        # initialize the table with User Defined Builds
        self.user_build_viewlist.AppendTextColumn("Build Name", width=150)
        self.user_build_viewlist.AppendTextColumn("Build Path", width=640)

        self.set_user_jobs_viewlist()
        self.set_cluster_load_table()

        # Disable Pre-Post/Interactive radio button in case of DCV
        if viz_type == "DCV":
            self.submit_mode_radiobox.EnableItem(3, False)
            self.submit_mode_radiobox.SetSelection(0)
        else:
            self.submit_mode_radiobox.EnableItem(3, True)
            self.submit_mode_radiobox.Select(3)

        self.m_notebook2.ChangeSelection(0)
        self.read_custom_builds()

        # populate UI with default or pre-saved settings
        if os.path.isfile(self.default_settings_json):
            try:
                self.settings_load()
                default_queue = self.default_settings["queue"]
            except KeyError:
                add_message("Settings file was corrupted", "Settings file", "!")

        init_combobox(queue_dict.keys(), self.queue_dropmenu, default_queue)
        self.select_queue()

        self.evt_node_list_check()
        self.on_reserve_check()

        # run in parallel to UI regular update of chart and process list
        self.running = True

        # bind custom event to invoke function on_signal
        self.Bind(SIGNAL_EVT, self.on_signal)
        self.Bind(SIGNAL_EVT_QSTAT, self.update_job_status)
        self.Bind(SIGNAL_EVT_LOG, self.add_log_entry)
        self.Bind(SIGNAL_EVT_BAR, self.set_status_bar)

        # start a thread to update cluster load
        worker = ClusterLoadUpdateThread(self)
        worker.start()

        self.m_nodes_list.Show(True)  # required for proper rendering
        # after UI is loaded run select_mode to process UI correctly, otherwise UI is shifted since sizers do not
        # reserve space for hidden objects
        wx.CallAfter(self.select_mode)

    def set_user_jobs_viewlist(self):
        """ Setup Process ViewList"""
        self.qstat_viewlist.AppendTextColumn("PID", width=70)
        self.qstat_viewlist.AppendTextColumn("State", width=50)
        self.qstat_viewlist.AppendTextColumn("Name", width=80)
        self.qstat_viewlist.AppendTextColumn("User", width=70)
        self.qstat_viewlist.AppendTextColumn("Queue", width=200)
        self.qstat_viewlist.AppendTextColumn("cpu", width=40)
        self.qstat_viewlist.AppendTextColumn("Started", width=50)

    def set_cluster_load_table(self):
        """ setup cluster load table"""
        self.load_grid.SetColLabelValue(0, "Available")
        self.load_grid.SetColSize(0, 80)
        self.load_grid.SetColLabelValue(1, "Used")
        self.load_grid.SetColSize(1, 80)
        self.load_grid.SetColLabelValue(2, "Reserved")
        self.load_grid.SetColSize(2, 80)
        self.load_grid.SetColLabelValue(3, "Failed")
        self.load_grid.SetColSize(3, 80)
        self.load_grid.SetColLabelValue(4, "Total")
        self.load_grid.SetColSize(4, 80)
        for i, queue_key in enumerate(queue_dict):
            self.load_grid.AppendRows(1)
            self.load_grid.SetRowLabelValue(i, queue_key)

            # colors
            self.load_grid.SetCellBackgroundColour(i, 0, "light green")
            self.load_grid.SetCellBackgroundColour(i, 1, "red")
            self.load_grid.SetCellBackgroundColour(i, 2, "light grey")

    def set_status_bar(self, _unused_event=None):
        self.m_status_bar.SetStatusText(self.bar_text, 1)
        self.m_status_bar.SetBackgroundColour(self.bar_color)
        self.m_status_bar.Refresh()

    def add_status_msg(self, msg="", level="i"):
        """
        Function that creates a thread to add a status bar message with alternating color to take attention of the user
        :param msg: str, message text
        :param level: either "i" as information for green color or "!" as error for red color
        :return: None
        """

        self.bar_text = msg
        self.bar_level = level
        self.bar_color = wx.WHITE

        # start a thread to update status bar
        self.worker = FlashStatusBarThread(self)
        self.worker.start()

    @staticmethod
    def ensure_app_folder():
        """Create a path for .aedt folder if first run

        Returns
        str
            Path to application directory.
        """

        user_dir = os.path.expanduser("~")
        app_dir = os.path.join(user_dir, ".aedt")
        if not os.path.exists(app_dir):
            try:
                os.makedirs(app_dir)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        return app_dir

    def on_signal(self, *args):
        """Update UI when signal comes from subthread. Should be updated always from main thread."""

        # run in list to keep order
        for i, queue_name in enumerate(queue_dict):
            self.load_grid.SetCellValue(i, 0, str(queue_dict[queue_name]["avail_cores"]))
            self.load_grid.SetCellValue(i, 1, str(queue_dict[queue_name]["used_cores"]))
            self.load_grid.SetCellValue(i, 2, str(queue_dict[queue_name]["reserved_cores"]))
            self.load_grid.SetCellValue(i, 3, str(queue_dict[queue_name]["failed_cores"]))
            self.load_grid.SetCellValue(i, 4, str(queue_dict[queue_name]["total_cores"]))

    def read_custom_builds(self):
        """Reads all specified in JSON file custom builds."""
        if os.path.isfile(self.user_build_json):
            try:
                with open(self.user_build_json) as file:
                    self.builds_data = json.load(file)
            except json.decoder.JSONDecodeError:
                print("JSON file with user builds is corrupted")
                os.remove(self.user_build_json)
                return

            for bld_version, bld_path in self.builds_data.items():
                prod_list_path = os.path.join(bld_path, "config", "ProductList.txt")
                if not os.path.isfile(prod_list_path):
                    print(f"Product is not available. Please check {bld_path}")
                    continue

                self.user_build_viewlist.AppendItem([bld_version, bld_path])
                install_dir[bld_version] = bld_path
                with open(prod_list_path) as file:
                    self.products[bld_version] = next(file).rstrip()  # get first line

            # update values in version selector on 1st page
            init_combobox(install_dir.keys(), self.m_select_version1, default_version)

    def write_custom_build(self):
        """Create a user JSON file with custom builds and to update selector."""

        num_rows = self.user_build_viewlist.GetItemCount()
        self.builds_data = {}

        for i in range(num_rows):
            self.builds_data[self.user_build_viewlist.GetTextValue(i, 0)] = self.user_build_viewlist.GetTextValue(i, 1)

        # update values in version selector on 1st page
        init_combobox(install_dir.keys(), self.m_select_version1, default_version)

        with open(self.user_build_json, "w") as file:
            json.dump(self.builds_data, file, indent=4)

    def settings_save(self, *args):
        """Take all values from the UI and dump them to the .json file."""
        self.default_settings = {
            "version": __version__,
            "queue": self.queue_dropmenu.GetValue(),
            "allocation": self.m_alloc_dropmenu.GetValue(),
            "num_cores": self.m_numcore.Value,
            "aedt_version": self.m_select_version1.Value,
            "env_var": self.env_var_text.Value,
            "use_node_list": self.m_nodes_list_checkbox.Value,
            "node_list": self.m_nodes_list.Value,
            "project_path": self.path_textbox.Value,
            "use_reservation": self.m_reserved_checkbox.Value,
            "reservation_id": self.reservation_id_text.Value,
        }

        with open(self.default_settings_json, "w") as file:
            json.dump(self.default_settings, file, indent=4)

    def settings_load(self):
        """Read settings file and populate UI with values."""

        with open(self.default_settings_json, "r") as file:
            self.default_settings = json.load(file)

        try:
            if self.default_settings["queue"] not in queue_config_dict:
                # if queue was deleted from cluster
                self.default_settings["queue"] = default_queue

            self.queue_dropmenu.Value = self.default_settings["queue"]
            self.m_numcore.Value = self.default_settings["num_cores"]
            self.m_select_version1.Value = self.default_settings["aedt_version"]
            self.env_var_text.Value = self.default_settings["env_var"]

            self.m_nodes_list.Value = self.default_settings.get("node_list", "")
            self.m_nodes_list_checkbox.Value = self.default_settings.get("use_node_list", False)

            self.path_textbox.Value = self.default_settings["project_path"]

            self.m_reserved_checkbox.Value = self.default_settings["use_reservation"]
            self.reservation_id_text.Value = self.default_settings["reservation_id"]

            queue_value = self.queue_dropmenu.GetValue()
            self.m_node_label.LabelText = self.construct_node_specs_str(queue_value)
        except wx._core.wxAssertionError:
            add_message(
                "UI was updated or default settings file was corrupted. Please save default settings again", "", "i"
            )

    @staticmethod
    def construct_node_specs_str(queue):
        """Construct node description string from cluster configuration data

        Parameters
        queue
            Queue for which we need a node description

        Returns
        -------
        str
            Human readable string for the UI with number of cores and
            RAM per node.
        """

        node_str = f"({queue_config_dict[queue]['cores']} Cores, {queue_config_dict[queue]['ram']}GB RAM per node)"
        return node_str

    def settings_reset(self, *args):
        """Remove settings previously set by user.

        Fired on click to reset to factory.
        """
        if os.path.isfile(self.default_settings_json):
            os.remove(self.default_settings_json)
            add_message("To complete resetting please close and start again the application", "", "i")

    def timer_stop(self):
        self.running = False

    def evt_num_cores_nodes_change(self, *args):
        try:
            num_cores = num_nodes = int(self.m_numcore.Value or 0)
        except ValueError:
            self.add_status_msg("Nodes Value must be integer", level="!")
            self.m_numcore.Value = str(1)
            return

        if num_cores < 0:
            self.m_numcore.Value = str(1)
            return

        cores_per_node = queue_config_dict[self.queue_dropmenu.Value]["cores"]
        ram_per_node = queue_config_dict[self.queue_dropmenu.Value]["ram"]
        if self.m_alloc_dropmenu.GetCurrentSelection() == 0:
            if num_cores > cores_per_node:
                self.m_numcore.Value = str(cores_per_node)
                # todo add status message
            summary_msg = f"You request {self.m_numcore.Value} Cores and {ram_per_node}GB of shared RAM"
        else:
            total_cores = cores_per_node * num_nodes
            total_ram = ram_per_node * num_nodes
            summary_msg = f"You request {total_cores} Cores and {total_ram}GB RAM"

        self.m_summary_caption.LabelText = summary_msg

    def evt_select_allocation(self, *args):
        """Callback when user changes allocation strategy."""
        if self.m_alloc_dropmenu.GetCurrentSelection() == 0:
            self.m_num_cores_caption.LabelText = "# Cores"
        else:
            self.m_num_cores_caption.LabelText = "# Nodes"

    def select_mode(self, *args):
        """Callback invoked on change of the mode Pre/Post or Interactive.

        Grey out options that are not applicable for Pre/Post.
        """
        sel = self.submit_mode_radiobox.Selection
        if sel == 3:
            enable = True

            self.m_nodes_list.Show(self.m_nodes_list_checkbox.Value)  # required for proper rendering
        else:
            enable = False
            self.m_nodes_list_checkbox.Value = False
            self.m_reserved_checkbox.Value = False
            self.reservation_id_text.Show(enable)
            self.m_nodes_list.Show(enable)

        self.m_summary_caption.Show(enable)
        self.queue_dropmenu.Show(enable)
        self.m_numcore.Show(enable)
        self.m_node_label.Show(enable)
        self.m_nodes_list_checkbox.Show(enable)
        self.m_alloc_dropmenu.Show(enable)
        self.m_num_cores_caption.Show(enable)
        self.m_alloc_caption.Show(enable)
        self.m_queue_caption.Show(enable)
        self.m_specify_nodes_caption.Show(enable)

        # todo remove if find a way to run reservation for Slurm batch
        self.m_reserved_checkbox.Show(enable)
        self.m_reservation_caption.Show(enable)

        # self.m_alloc_dropmenu.Enable(enable)  # todo enable if Slurm will support non-exclusive
        self.evt_select_allocation()
        self.evt_num_cores_nodes_change()

    def update_job_status(self, *args):
        """Event is called to update a viewlist with current running jobs from main thread (thread safety)."""
        self.qstat_viewlist.DeleteAllItems()
        for q_dict in qstat_list:
            self.qstat_viewlist.AppendItem(
                [
                    q_dict["pid"],
                    q_dict["state"],
                    q_dict["name"],
                    q_dict["user"],
                    q_dict["queue_data"],
                    q_dict["proc"],
                    q_dict["started"],
                ]
            )

    def update_msg_list(self):
        """Update messages on checkbox and init from file"""
        self.scheduler_msg_viewlist.DeleteAllItems()
        for msg in self.log_data["Message List"]:
            sched = msg[3]
            if sched or self.m_checkBox_allmsg.Value:
                tab_data = msg[0:3]
                self.scheduler_msg_viewlist.PrependItem(tab_data)

    def add_log_entry(self, *args):
        """Add new entry to the Scheduler Messages Window."""
        scheduler = log_dict.get("scheduler", True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = wordwrap(log_dict["msg"], 600, wx.ClientDC(self))
        data = [timestamp, log_dict.get("pid", "0"), message, scheduler]

        if scheduler or self.m_checkBox_allmsg.Value:
            tab_data = data[0:3]
            self.scheduler_msg_viewlist.PrependItem(tab_data)
        self.log_data["Message List"].append(data)
        with open(self.logfile, "w") as fa:
            json.dump(self.log_data, fa, indent=4)

    def rmb_on_scheduler_msg_list(self, *args):
        """When clicking RMB on the scheduler message list it will
        propose a context menu with choice to delete all messages.
        """
        position = wx.ContextMenuEvent(type=wx.wxEVT_NULL)
        self.PopupMenu(ClearMsgPopupMenu(self), position.GetPosition())

    def leftclick_processtable(self, *args):
        """On double click on process row will propose to abort running job"""
        self.cancel_job()

    def cancel_job(self):
        """
        Send Slurm scancel command
        :return:
        """
        row = self.qstat_viewlist.GetSelectedRow()
        pid = self.qstat_viewlist.GetTextValue(row, 0)
        result = add_message("Abort Queue Process {}?\n".format(pid), "Confirm Abort", "?")
        if result == wx.ID_OK:
            command = f"scancel {pid}"
            subprocess.call(command, shell=True)
            print(f"Job cancelled via: {command}")

            msg = "Job {} cancelled from GUI".format(pid)
            try:
                self.log_data["PID List"].remove(pid)
            except ValueError:
                pass

            log_dict["pid"] = pid
            log_dict["msg"] = msg
            log_dict["scheduler"] = False
            self.add_log_entry()

    def select_queue(self, *args):
        """Called when user selects a value in Queue drop down menu.

        Also called during __init__ to fill the UI.  Sets PE and
        number of cores for each queue.
        """
        queue_value = self.queue_dropmenu.GetValue()

        self.m_node_label.LabelText = self.construct_node_specs_str(queue_value)
        self.evt_num_cores_nodes_change()

    def evt_node_list_check(self, *args):
        """Callback called when clicked "Specify node list" options.

        Hides/Shows input field for node list.
        """
        if self.m_nodes_list_checkbox.Value:
            self.m_nodes_list.Show()
        else:
            self.m_nodes_list.Hide()

    def on_reserve_check(self, *args):
        """Callback called when clicked Reservation.

        Will Hide/Show input field for reservation ID.
        """
        if self.m_reserved_checkbox.Value:
            self.reservation_id_text.Show()
        else:
            self.reservation_id_text.Hide()

    def submit_overwatch_thread(self, *args):
        """Opens OverWatch on button click"""
        if not os.path.isfile(FIREFOX):
            add_message("Firefox is not installed on the cluster", title="Error", icon="!")
            return

        threading.Thread(target=self.open_overwatch, daemon=True).start()

    def check_display_var(self):
        """Validate that DISPLAY variable follow convention hostname:display_number

        Returns
        -------
        str
            Proper display value
        """

        display_var = os.getenv("DISPLAY", "")
        if not display_var:
            msg = "DISPLAY environment variable is not specified. Contact cluster admin"
            add_message(msg, "Environment error", icon="!")
            raise EnvironmentError(msg)

        if ":" not in display_var:
            msg = "DISPLAY hasn't session number specified. Contact cluster admin"
            add_message(msg, "Environment error", icon="!")
            raise EnvironmentError(msg)

        if not display_var.split(":")[0]:
            return f"{self.hostname}:{display_var.split(':')[1]}"

        return display_var

    def click_launch(self, *args):
        """Depending on the choice of the user invokes AEDT on visual node or simply for pre/post"""
        check_ssh()

        aedt_version = self.m_select_version1.Value
        aedt_path = install_dir[aedt_version]

        env = ""
        if self.env_var_text.Value:
            env += "" + self.env_var_text.Value

        if admin_env_vars:
            env_list = [f"{env_var}={env_val}" for env_var, env_val in admin_env_vars.items()]
            env += "," + ",".join(env_list)

        # verify that no double commas, spaces, etc
        if env:
            env = re.sub(" ", "", env)
            env = re.sub(",+", ",", env)
            env = env.rstrip(",").lstrip(",")

        reservation, reservation_id = self.check_reservation()
        if reservation and not reservation_id:
            return

        try:
            self.update_registry(aedt_path)
        except FileNotFoundError:
            add_message("Verify project directory. Probably user name was changed", "Wrong project path", "!")
            return

        op_mode = self.submit_mode_radiobox.GetSelection()

        job_type = {0: "pre-post", 1: "monitor", 2: "submit", 3: "interactive"}
        try:
            self.send_statistics(aedt_version, job_type[op_mode])
        except:
            # not worry a lot
            print("Error sending statistics")

        if op_mode == 3:
            self.submit_interactive_job(aedt_path, env, reservation, reservation_id)
        else:
            env = env[4:]  # remove ALL, from env vars
            command_key = ""
            if op_mode == 1:
                command_key = "-showsubmitjob"
            elif op_mode == 2:
                command_key = "-showmonitorjob"

            threading.Thread(
                target=self._submit_batch_thread,
                daemon=True,
                args=(
                    aedt_path,
                    env,
                    command_key,
                ),
            ).start()

    def submit_interactive_job(self, aedt_path, env, reservation, reservation_id):
        """
        Submit interactive job
        :param aedt_path:
        :param env:
        :param reservation:
        :param reservation_id:
        :return: None
        """

        scheduler = "sbatch"
        allocation_rule = self.m_alloc_dropmenu.GetCurrentSelection()
        if int(self.m_numcore.Value or 0) < 1:
            self.add_status_msg("Nodes Value must be a positive integer", level="!")
            return

        num_nodes = num_cores = int(self.m_numcore.Value)
        queue = self.queue_dropmenu.Value

        # interactive submission
        env += f",DISPLAY={self.display_node}"

        command = [scheduler, "--job-name", "aedt", "--partition", queue, "--export", env]
        if allocation_rule == 0:
            # 1 node and cores
            command += ["--nodes", "1-1", "--ntasks", str(num_cores)]
            total_cores = num_cores
        else:
            cores_per_node = queue_config_dict[queue]["cores"]
            total_cores = cores_per_node * num_nodes
            command += ["--nodes", f"{num_nodes}-{num_nodes}", "--ntasks", str(total_cores)]

        nodes_list_str = self.m_nodes_list.Value
        nodes_list_str = nodes_list_str.replace(" ", "")

        if self.m_nodes_list_checkbox.Value and nodes_list_str:
            command += ["--nodelist", nodes_list_str]

        if reservation:
            command += ["--reservation", reservation_id]

        aedt_str = " ".join([os.path.join(aedt_path, "ansysedt"), "-machinelist", f"num={total_cores}"])
        command += ["--wrap", f'"{aedt_str}"']
        command = " ".join(command)  # convert to string to avoid escaping characters
        print(f"Execute via: {command}")

        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        except subprocess.CalledProcessError as exc:
            msg = exc.output
            log_dict["scheduler"] = True
        else:
            msg = f"Job submitted to {queue}\nSubmit Command:{command}"
            pid = output.strip().split()[-1]
            log_dict["scheduler"] = False
            log_dict["pid"] = pid
            self.log_data["PID List"].append(pid)

        log_dict["msg"] = msg
        self.add_log_entry()

    def check_reservation(self):
        """Validate if user wants to run with predefined reservation.

        Create a reservation argument for interactive mode or create
        .sge_request file with argument for non graphical

        Returns
        -------
        bool
            ``True`` if reservation was checked AND reservation ID if the
            value is correct.
        str
            Reservation ID.
        """
        reservation = self.m_reserved_checkbox.Value
        ar = ""
        if reservation:
            ar = self.reservation_id_text.Value
            if ar in [None, ""]:
                add_message(
                    "Reservation ID is not provided. Please set ID and click launch again", "Reservation ID", "!"
                )

        return reservation, ar

    def send_statistics(self, version, job_type):
        """Send usage statistics to the database.

        Parameters
        ----------
        version : str
            Version of EDT used.

        job_type : str
            Interactive or non-graphical job type.

        """
        if DEBUG_MODE:
            return

        client = InfluxDBClient(host=STATISTICS_SERVER, port=STATISTICS_PORT)
        db_name = "aedt_hpc_launcher"
        client.switch_database(db_name)

        time_now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        json_body = [
            {
                "measurement": db_name,
                "tags": {
                    "username": self.username,
                    "version": version,
                    "job_type": job_type,
                    "cluster": self.hostname[:3],
                },
                "time": time_now,
                "fields": {"count": 1},
            }
        ]

        client.write_points(json_body)

    def update_registry(self, aedt_path):
        """Set registry for each run of EDT.

        This is necessary because each run occurs on a different Linux node.

        Disables:
        1. Question on product improvement
        2. Question on Project directory, this is grabbed from UI
        3. Welcome message
        4. Question on personal lib

        Sets:
        1. EDT Installation path
        2. Slurm scheduler as default

        aedt_path : str
            Path to the installation directory of EDT.
        """
        if not os.path.isdir(self.path_textbox.Value):
            os.mkdir(self.path_textbox.Value)

        commands = []  # list to aggregate all commands to execute
        registry_file = os.path.join(aedt_path, "UpdateRegistry")

        # set base for each command: path to registry, product and level
        command_base = [
            registry_file,
            "-Set",
            "-ProductName",
            self.products[self.m_select_version1.Value],
            "-RegistryLevel",
            "user",
        ]

        # disable question about participation in product improvement
        commands.append(
            ["-RegistryKey", "Desktop/Settings/ProjectOptions/ProductImprovementOptStatus", "-RegistryValue", "1"]
        )

        # set installation path
        commands.append(["-RegistryKey", "Desktop/InstallationDirectory", "-RegistryValue", aedt_path])

        # set project folder
        commands.append(["-RegistryKey", "Desktop/ProjectDirectory", "-RegistryValue", self.path_textbox.Value])

        # disable welcome message
        commands.append(["-RegistryKey", "Desktop/Settings/ProjectOptions/ShowWelcomeMsg", "-RegistryValue", "0"])

        # set personal lib
        personal_lib = os.path.join(os.environ["HOME"], "Ansoft", "Personallib")
        commands.append(["-RegistryKey", "Desktop/PersonalLib", "-RegistryValue", personal_lib])

        # set Slurm scheduler
        settings_areg = os.path.join(os.path.dirname(os.path.realpath(__file__)), "slurm_settings.areg")
        commands.append(["-FromFile", settings_areg])

        for command in commands:
            subprocess.call(command_base + command)

    def m_update_msg_list(self, *args):
        """Fired when user clicks 'Show all messages' for Scheduler messages window"""
        self.update_msg_list()

    def delete_row(self, *args):
        """By clicking on Delete Row button delete row and rewrite json file with builds"""
        row = self.user_build_viewlist.GetSelectedRow()
        if row != -1:
            self.user_build_viewlist.DeleteItem(row)
            self.write_custom_build()

    def add_new_build(self, *args):
        """By click on Add New Build opens file dialogue to select path and input box to set name.
        At the end we update JSON file with custom builds"""
        get_dir_dialogue = wx.DirDialog(
            None, "Choose a Linux64 directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
        )
        if get_dir_dialogue.ShowModal() == wx.ID_OK:
            path = get_dir_dialogue.GetPath()
            get_dir_dialogue.Destroy()
        else:
            get_dir_dialogue.Destroy()
            return

        if "Linux64" not in path[-7:]:
            add_message(
                "Your path should include and be ended by Linux64 (eg /ott/apps/ANSYSEM/Linux64)", "Wrong path", "!"
            )
            return

        get_name_dialogue = wx.TextEntryDialog(None, "Set name of a build:", value="AEDT_2019R3")
        if get_name_dialogue.ShowModal() == wx.ID_OK:
            name = get_name_dialogue.GetValue()
            get_name_dialogue.Destroy()
        else:
            get_name_dialogue.Destroy()
            return

        if name in [None, ""] + list(self.builds_data.keys()):
            add_message("Name cannot be empty and not unique", "Wrong name", "!")
            return

        # if all is fine add new build
        self.user_build_viewlist.AppendItem([name, path])
        install_dir[name] = path

        with open(os.path.join(path, "config", "ProductList.txt")) as file:
            self.products[name] = next(file).rstrip()  # get first line

        self.write_custom_build()

    def set_project_path(self, *args):
        """Invoked when clicked on "..." set_path_button.

        Creates a dialogue where user can select directory.
        """
        get_dir_dialogue = wx.DirDialog(None, "Choose directory:", style=wx.DD_DEFAULT_STYLE)
        if get_dir_dialogue.ShowModal() == wx.ID_OK:
            path = get_dir_dialogue.GetPath()
            get_dir_dialogue.Destroy()
        else:
            get_dir_dialogue.Destroy()
            return

        self.path_textbox.Value = path

    def shutdown_app(self, *args):
        """Exit from app by clicking X or Close button.

        Kill the process to kill all child threads.
        """
        self.timer_stop()
        lock_file = os.path.join(self.app_dir, "ui.lock")
        try:
            os.remove(lock_file)
        except FileNotFoundError:
            pass

        while len(threading.enumerate()) > 1:  # possible solution to wait until all threads are dead
            time.sleep(0.25)

        signal.pthread_kill(threading.get_ident(), signal.SIGINT)
        os.kill(os.getpid(), signal.SIGINT)

    def open_overwatch(self):
        """Open Overwatch with java."""
        command = [FIREFOX, f"{overwatch_url}/users/{self.username}"]
        subprocess.call(command)

    @staticmethod
    def _submit_batch_thread(aedt_path, env, command_key):
        """Start EDT in pre/post mode.

        Parameters
        ----------
        aedt_path : str
            Path to the EDT root.
        env : str
            String with list of environment variables.
        command_key :
            Add key to open Submit or Monitor Job dialog.
        """

        env_vars = os.environ.copy()
        if env:
            for var_value in env.split(","):
                variable, value = var_value.split("=")
                env_vars[variable] = value

        command = [os.path.join(aedt_path, "ansysedt"), command_key]
        print("Electronics Desktop is started via:", subprocess.list2cmdline(command))
        subprocess.Popen(command, env=env_vars)


def check_ssh():
    """Verify that all passwordless SSH are in place."""
    ssh_path = os.path.join(os.environ["HOME"], ".ssh")
    for file in ["authorized_keys", "config"]:
        if not os.path.isfile(os.path.join(ssh_path, file)):
            if os.path.isdir(ssh_path):
                shutil.rmtree(ssh_path)

            proc = subprocess.Popen([path_to_ssh], stdin=subprocess.PIPE, shell=True)
            proc.communicate(input=b"\n\n\n")
            break


def add_message(message, title="", icon="?"):
    """Create a dialog with different set of buttons.

    Parameters
    ----------
    message : str
        Message you want to show.
    title : str, optional
        Message window title.
    icon : str, optional
        Depending on the input will create either question dialogue
        (?), error (!) or just an information dialog.

    Returns
    -------
    int
        Response from the user (for example, wx.OK).
    """

    if icon == "?":
        icon = wx.OK | wx.CANCEL | wx.ICON_QUESTION
    elif icon == "!":
        icon = wx.OK | wx.ICON_ERROR
    else:
        icon = wx.OK | wx.ICON_INFORMATION

    dlg_qdel = wx.MessageDialog(None, message, title, icon)
    result = dlg_qdel.ShowModal()
    dlg_qdel.Destroy()

    return result


def init_combobox(entry_list, combobox, default_value=""):
    """Fills a wx.Combobox element with the entries in a list.

    Parameters
    ----------
    entry_list : list
        List of text entries to appear in the combobox element.
    combobox : wx.Combobox
        object pointing to the combobox element
    default_value : str, optional
        Default value (must be present in the entry list, otherwise
        will be ignored)

    """
    combobox.Clear()
    index = 0
    for i, value in enumerate(list(entry_list)):
        if value == default_value:
            index = i
        combobox.Append(value)
    combobox.SetSelection(index)


def main():
    """Main function to generate UI.

    Validate that only one instance is opened.
    """
    # this 0.7 sleep prevents double open if user has single click launch in Linux and performs double click
    time.sleep(0.7)

    app = wx.App()

    lock_file = os.path.join(LauncherWindow.ensure_app_folder(), "ui.lock")
    if os.path.exists(lock_file):
        result = add_message(
            (
                "Application was not properly closed or you have multiple instances opened. "
                "Do you really want to open new instance?"
            ),
            "Instance error",
            "?",
        )
        if result != wx.ID_OK:
            return
    else:
        with open(lock_file, "w") as file:
            file.write("1")

    ex = LauncherWindow(None)
    ex.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
