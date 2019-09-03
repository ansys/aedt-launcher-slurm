from src_gui import GUIFrame
from datetime import datetime
from tendo import singleton
from collections import OrderedDict

import xml.etree.ElementTree as ET

import signal
import os
import getpass
import socket
import errno
import json
import subprocess
import time
import threading
import wx
import wx.dataview
import wx._core
import shutil
import re

__authors__ = "Leon Voss, Maksim Beliaev"
__version__ = "v2.0"

# Simple dictionary for the versions (* at the beginning) for the default version
default_version = u"2019 R3"
install_dir = OrderedDict([
    (u"R18.2",   '/ott/apps/software/ANSYS_EM_182/AnsysEM18.2/Linux64'),
    (u"R19.0",   '/ott/apps/software/ANSYS_EM_190/AnsysEM19.0/Linux64'),
    (u"R19.1",   '/ott/apps/software/ANSYS_EM_191/AnsysEM19.1/Linux64'),
    (u"R19.2",   '/ott/apps/software/ANSYS_EM_192/AnsysEM19.2/Linux64'),
    (u"2019 R1", '/ott/apps/software/ANSYS_EM_2019R1/AnsysEM19.3/Linux64'),
    (u"2019 R2", '/ott/apps/software/ANSYS_EM_2019R2/AnsysEM19.4/Linux64'),
    (u"2019 R3", '/ott/apps/software/ANSYS_EM_2019R3/AnsysEM19.5/Linux64')
])

# Define default number of cores for the selected PE (interactive mode)
pe_cores = {
    'electronics-2': 2,
    'electronics-4': 4,
    'electronics-8': 8,
    'electronics-16': 16,
    'electronics-20': 20,
    'electronics-28': 28
}

node_config_str = {
    'euc09':    '(20 cores, 128GB  / node)',
    'ottc01':   '(28 cores, 128GB  / node)',
    'euc09lm':  '(28 cores, 512GB  / node)'
}

default_queue = u'euc09'
queue_dict = {
  "euc09": {"total_cores": 100,
            "avail_cores": 0,
            "used_cores": 100,
            "reserved_cores": 0,
            "failed_cores": 0,
            "parallel_env": ['electronics-2', 'electronics-4', 'electronics-8', 'electronics-16', 'electronics-20'],
            "default_pe": 'electronics-4'
            },
  "ottc01": {"total_cores": 100,
             "avail_cores": 0,
             "used_cores": 100,
             "reserved_cores": 0,
             "failed_cores": 0,
             "parallel_env": ['electronics-2', 'electronics-4', 'electronics-8', 'electronics-16', 'electronics-28'],
             "default_pe": 'electronics-4'
             },
  "euc09lm": {"total_cores": 100,
              "avail_cores": 0,
              "used_cores": 100,
              "reserved_cores": 0,
              "failed_cores": 0,
              "parallel_env": ['electronics-2', 'electronics-4', 'electronics-8', 'electronics-16', 'electronics-28'],
              "default_pe": 'electronics-4'
              }
}

class ClearMsgPopupMenu(wx.Menu):
    def __init__(self, parent):
        super(ClearMsgPopupMenu, self).__init__()

        self.parent = parent

        mmi = wx.MenuItem(self, wx.NewId(), 'Clear All Messages')
        self.Append(mmi)
        self.Bind(wx.EVT_MENU, self.on_clear, mmi)

    def on_clear(self, _unused):
        self.parent.scheduler_msg_viewlist.DeleteAllItems()
        self.parent.log_data = {"Message List": [],
                                "PID List": [],
                                "GUI Data": []}

        if os.path.isfile(self.parent.logfile):
            os.remove(self.parent.logfile)


# create a new event to bind it and call it from subthread. UI should be changed ONLY in MAIN THREAD
ID_COUNT = wx.NewId()
my_SIGNAL_EVT = wx.NewEventType()
SIGNAL_EVT = wx.PyEventBinder(my_SIGNAL_EVT, 1)

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
        """Overrides Thread.run. Don't call this directly its called internally
        when you call Thread.start().

        Gets cluster load every 60 seconds. 0.5s step is used to be able to stop subthread earlier
        by triggering parent.running
        """
        counter = 120
        while self._parent.running:
            if counter % 120 == 0:
                xml_file = os.path.join(self._parent.user_dir, '.aedt', "data.xml")
                out_file = os.path.join(self._parent.user_dir, '.aedt', "dump.txt")
                command = "java -jar /ott/apps/software/AEDT_Launcher/overwatch.jar -xmlpath {} >& {}".format(xml_file,
                                                                                                              out_file)
                subprocess.call(command, shell=True)
                with open(xml_file, "r") as file:
                    data = file.read()
                q_statistics = ET.fromstring(data)

                """
                 Example of output of qstat -g c
                CLUSTER QUEUE                   CQLOAD   USED    RES  AVAIL  TOTAL aoACDS  cdsuE
                --------------------------------------------------------------------------------
                all.q                             -NA-      0      0      0      0      0      0
                dcv                               0.64     32      0      4     36      0      0
                euc09                             0.47    742      0    218    960      0      0
                euc09gpu                          0.00      0      0     56     56      0      0
                euc09lm                           0.37     56      0     84    140     28      0
                ottc01                            0.43   1040      0    276   1344      0     28
                vnc                               0.63     35      0     37     72      0      0
                """

                for queue_elem in q_statistics.findall("Queues/Queue"):
                    queue_name = queue_elem.get("name")
                    if queue_name in ["euc09", "ottc01", "euc09lm"]:
                        total_cores = 0
                        used_cores = 0
                        reserved_cores = 0
                        failed_cores = 0
                        for host in queue_elem.findall("Hosts/Host"):
                            total = host.find("Slots/Total").text
                            total_cores += int(total)

                            if host.find("State").text in ["E", "d", "D", "s", "S", "u"]:
                                failed_cores += int(total)
                            elif int(host.find("Slots/Reserved").text) > 0:
                                reserved_cores += int(total)
                            elif host.find("Exclusive").text == "true":
                                used_cores += int(total)
                            else:
                                used_cores += int(host.find("Slots/Used").text)

                        available_cores = total_cores - failed_cores - reserved_cores - used_cores

                        queue_dict[queue_name]["total_cores"] = total_cores
                        queue_dict[queue_name]["used_cores"] = used_cores
                        queue_dict[queue_name]["failed_cores"] = failed_cores
                        queue_dict[queue_name]["reserved_cores"] = reserved_cores
                        queue_dict[queue_name]["avail_cores"] = available_cores

                evt = SignalEvent(my_SIGNAL_EVT, -1)
                wx.PostEvent(self._parent, evt)

                counter = 0
            time.sleep(0.5)
            counter += 1


class MyWindow(GUIFrame):
    def __init__(self, parent):
        # Initialize the main form
        GUIFrame.__init__(self, parent)

        # Get environment data
        self.user_dir = os.path.expanduser('~')
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.display_node = os.getenv('DISPLAY')
        self.qstat = "/ott/apps/uge/bin/lx-amd64/qstat"

        # get paths
        self.user_build_json = os.path.join(self.user_dir, '.aedt', 'user_build.json')
        self.default_settings_json = os.path.join(self.user_dir, '.aedt', 'default.json')
        
        self.builds_data = {}
        self.default_settings = {}

        # generate list of products for registry
        self.products = {}
        for key in install_dir.keys():
            with open(os.path.join(install_dir[key], "config", "ProductList.txt")) as file:
                self.products[key] = next(file).rstrip()  # get first line

        # set default project path
        self.path_textbox.Value = os.path.join(os.environ["HOME"], "EDT_projects")

        if self.display_node[0] == ':':
            self.display_node = self.hostname + self.display_node

        vnc_nodes = ['ottvnc']
        dcv_nodes = ['eurgs']
        viz_type = None
        for x in vnc_nodes:
            if x in self.display_node:
                viz_type = 'VNC'
                break
        if viz_type is None:
            for x in dcv_nodes:
                if x in self.display_node:
                    viz_type = 'DCV'
                    break

        msg = 'No Status Message'
        if viz_type is None:
            msg = "Warning: Unknown Display Type!!"
            viz_type = ''

        if not os.path.exists(os.path.dirname(self.user_build_json)):
            try:
                os.makedirs(os.path.dirname(self.user_build_json))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        # Set the status bars on the bottom of the window
        self.m_statusBar1.SetStatusText('User: ' + self.username + ' on ' + viz_type + ' node ' + self.display_node, 0)
        self.m_statusBar1.SetStatusText(msg, 1)
        self.m_statusBar1.SetStatusWidths([500, -1])

        # create a list of default environmental variables
        init_combobox(install_dir.keys(), self.m_select_version1, default_version)

        self.interactive_env = ",".join(["DISPLAY=" + self.display_node, "LIBGL_ALWAYS_INDIRECT=True",
                                         "LIBGL_ALWAYS_SOFTWARE=True", "GALLIUM_DRIVER=swr", "ANS_NODEPCHECK=1"])

        self.advanced_options_text.Value = self.interactive_env

        self.local_env = "ANS_NODEPCHECK=1"


        # Setup Process Log
        self.scheduler_msg_viewlist.AppendTextColumn('Timestamp', width=140)
        self.scheduler_msg_viewlist.AppendTextColumn('PID', width=50)
        self.scheduler_msg_viewlist.AppendTextColumn('Message', width=400)
        self.logfile = os.path.join(self.user_dir, '.aedt', 'user_log_'+viz_type+'.json')

        # read in previous log file
        if os.path.exists(self.logfile):
            with open(self.logfile, 'r') as fi:
                self.log_data = json.load(fi)
                self.update_msg_list()
        else:
            self.log_data = {"Message List": [],
                             "PID List": [],
                             "GUI Data": []}

        # initialize the table with User Defined Builds
        self.user_build_viewlist.AppendTextColumn('Build Name', width=150)
        self.user_build_viewlist.AppendTextColumn('Build Path', width=640)

        # Setup Process ViewList
        self.qstat_viewlist.AppendTextColumn('PID', width=50)
        self.qstat_viewlist.AppendTextColumn('State', width=50)
        self.qstat_viewlist.AppendTextColumn('Name', width=80)
        self.qstat_viewlist.AppendTextColumn('User', width=50)
        self.qstat_viewlist.AppendTextColumn('Queue', width=200)
        self.qstat_viewlist.AppendTextColumn('cpu', width=30)
        self.qstat_viewlist.AppendTextColumn('Started', width=50)

        # setup cluster load
        self.load_grid.SetColLabelValue(0, 'Available')
        self.load_grid.SetColSize(0, 80)
        self.load_grid.SetColLabelValue(1, 'Used')
        self.load_grid.SetColSize(1, 80)
        self.load_grid.SetColLabelValue(2, 'Reserved')
        self.load_grid.SetColSize(2, 80)
        self.load_grid.SetColLabelValue(3, 'Failed')
        self.load_grid.SetColSize(3, 80)
        self.load_grid.SetColLabelValue(4, 'Total')
        self.load_grid.SetColSize(4, 80)

        self.load_grid.SetRowLabelValue(0, "euc09")
        self.load_grid.SetRowLabelValue(1, "ottc01")
        self.load_grid.SetRowLabelValue(2, "euc09lm")

        # colors
        self.load_grid.SetCellBackgroundColour(0, 0, "light green")
        self.load_grid.SetCellBackgroundColour(1, 0, "light green")
        self.load_grid.SetCellBackgroundColour(2, 0, "light green")

        self.load_grid.SetCellBackgroundColour(0, 1, "red")
        self.load_grid.SetCellBackgroundColour(1, 1, "red")
        self.load_grid.SetCellBackgroundColour(2, 1, "red")

        self.load_grid.SetCellBackgroundColour(0, 2, "light grey")
        self.load_grid.SetCellBackgroundColour(1, 2, "light grey")
        self.load_grid.SetCellBackgroundColour(2, 2, "light grey")

        # Disable Batch-mode radio button
        if viz_type == 'DCV':
            self.submit_mode_radiobox.EnableItem(1, False)
            self.submit_mode_radiobox.Select(0)
        else:
            self.submit_mode_radiobox.EnableItem(1, True)
            self.submit_mode_radiobox.Select(1)

        self.select_mode(None)
        self.m_notebook2.ChangeSelection(0)
        self.advanced_options_text.Hide()  # hide on start since hidden attribute is not working in wxBuilder
        self.read_custom_builds()

        if os.path.isfile(self.default_settings_json):
            try:
                self.set_default_settings()
                default_queue = self.default_settings["queue"]
            except KeyError:
                add_message("Settings file was corrupted", "Settings file", "!")

        init_combobox(queue_dict.keys(), self.queue_dropmenu, default_queue)

        self.queue_dropmenu.Value = default_queue
        self.select_queue(None)

        self.on_reserve_check(None)

        # run in parallel to UI regular update of chart and process list
        self.running = True
        threading.Thread(target=self.update_process_list, daemon=True).start()

        # bind custom event to invoke function on_signal
        self.Bind(SIGNAL_EVT, self.on_signal)

        # start a thread to update cluster load
        worker = ClusterLoadUpdateThread(self)
        worker.start()

    def on_signal(self, evt):
        """Update UI when signal comes from subthread. Should be updated always from main thread"""
        # run in list to keep order
        for i, queue_name in enumerate(["euc09", "ottc01", "euc09lm"]):
            self.load_grid.SetCellValue(i, 0, str(queue_dict[queue_name]["avail_cores"]))
            self.load_grid.SetCellValue(i, 1, str(queue_dict[queue_name]["used_cores"]))
            self.load_grid.SetCellValue(i, 2, str(queue_dict[queue_name]["reserved_cores"]))
            self.load_grid.SetCellValue(i, 3, str(queue_dict[queue_name]["failed_cores"]))
            self.load_grid.SetCellValue(i, 4, str(queue_dict[queue_name]["total_cores"]))

    def read_custom_builds(self):
        """Reads all specified in JSON file custom builds"""
        if os.path.isfile(self.user_build_json):
            with open(self.user_build_json) as file:
                self.builds_data = json.load(file)

            for key in self.builds_data.keys():
                self.user_build_viewlist.AppendItem([key, self.builds_data[key]])
                install_dir[key] = self.builds_data[key]
                with open(os.path.join(self.builds_data[key], "config", "ProductList.txt")) as file:
                    self.products[key] = next(file).rstrip()  # get first line

            # update values in version selector on 1st page
            init_combobox(list(install_dir.keys()), self.m_select_version1,
                          default_version)

    def write_custom_build(self):
        """Function to create a user JSON file with custom builds and to update selector"""
        num_rows = self.user_build_viewlist.GetItemCount()
        self.builds_data = {}

        for i in range(num_rows):
            self.builds_data[self.user_build_viewlist.GetTextValue(i, 0)] = self.user_build_viewlist.GetTextValue(i, 1)

        # update values in version selector on 1st page
        init_combobox(list(install_dir.keys()), self.m_select_version1, default_version)

        with open(self.user_build_json, "w") as file:
            json.dump(self.builds_data, file)

    def save_default_settings(self, _unused):
        self.default_settings = {
            "mode": self.submit_mode_radiobox.Selection,
            "queue": self.queue_dropmenu.GetValue(),
            "parallel_env": self.pe_dropmenu.GetValue(),
            "num_cores": self.m_numcore.Value,
            # "exclusive": self.exclusive_usage_checkbox.Value,
            "aedt_version": self.m_select_version1.Value,
            "env_var": self.env_var_text.Value,
            "advanced": self.advanced_options_text.Value,
            "project_path": self.path_textbox.Value,
            "use_reservation": self.reserved_checkbox.Value,
            "reservation_id": self.reservation_id_text.Value
        }

        with open(self.default_settings_json, "w") as file:
            json.dump(self.default_settings, file, indent=4)

    def set_default_settings(self):
        with open(self.default_settings_json, "r") as file:
            self.default_settings = json.load(file)

        try:
            self.submit_mode_radiobox.Selection = self.default_settings["mode"]
            self.queue_dropmenu.Value = self.default_settings["queue"]
            self.pe_dropmenu.Value = self.default_settings["parallel_env"]
            self.m_numcore.Value = self.default_settings["num_cores"]
            # self.exclusive_usage_checkbox.Value = self.default_settings["exclusive"]
            self.m_select_version1.Value = self.default_settings["aedt_version"]
            self.env_var_text.Value = self.default_settings["env_var"]
            self.advanced_options_text.Value = self.default_settings["advanced"]
            self.path_textbox.Value = self.default_settings["project_path"]

            self.reserved_checkbox.Value = self.default_settings["use_reservation"]
            self.reservation_id_text.Value = self.default_settings["reservation_id"]

            queue_value = self.queue_dropmenu.GetValue()
            self.m_node_label.LabelText = node_config_str[queue_value]
        except wx._core.wxAssertionError:
            add_message("UI was updated or default settings file was corrupted. Please save default settings again",
                        "", "i")

    def reset_settings(self, _unused):
        if os.path.isfile(self.default_settings_json):
            os.remove(self.default_settings_json)
            add_message("To complete resetting please close and start again the application", "", "i")

    def timer_stop(self):
        self.running = False

    def select_pe(self, _unused):
        """ Callback for the selection of parallel environment. Primarily used to set an appropriate number of cores"""
        pe_val = self.pe_dropmenu.Value
        core_val = pe_cores[pe_val]
        self.m_numcore.Value = str(core_val)

    def select_mode(self, _unused):
        """Callback invoked on change of the mode Pre/Post or Interactive"""
        sel = self.submit_mode_radiobox.Selection
        if sel == 0:
            enable = False
            self.reserved_checkbox.Value = enable
            self.advanced_options_text.Value = self.local_env
        else:
            enable = True
            self.advanced_options_text.Value = self.interactive_env

        self.reserved_checkbox.Enabled = enable
        self.queue_dropmenu.Enabled = enable
        self.m_numcore.Enabled = enable
        # self.exclusive_usage_checkbox.Enabled = enable
        self.m_node_label.Enabled = enable
        self.pe_dropmenu.Enable(enable)

        self.on_reserve_check(None)

    def update_msg_list(self):
        """Update messages on checkbox and init from file"""
        self.scheduler_msg_viewlist.DeleteAllItems()
        for msg in self.log_data["Message List"]:
            sched = msg[3]
            if sched or self.m_checkBox_allmsg.Value:
                tab_data = msg[0:3]
                self.scheduler_msg_viewlist.PrependItem(tab_data)

    def add_log_entry(self, pid, msg, scheduler=False):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = [timestamp, pid, msg, scheduler]
        if scheduler or self.m_checkBox_allmsg.Value:
            tab_data = data[0:3]
            self.scheduler_msg_viewlist.PrependItem(tab_data)
        self.log_data["Message List"].append(data)
        with open(self.logfile, 'w') as fa:
            json.dump(self.log_data, fa)

    def update_process_list(self):
        """Update a list of jobs status for a user every 5s"""
        counter = 10
        while self.running:
            if counter % 10 == 0:
                qstat_output = subprocess.check_output(self.qstat, shell=True).decode("ascii", errors="ignore")
                self.qstat_viewlist.DeleteAllItems()

                exclude = ['VNC Deskto', 'DCV Deskto']
                for i, line in enumerate(qstat_output.split("\n")):
                    if i > 1:
                        pid = line[0:10].strip()
                        # prior = line[11:18].strip()
                        name = line[19:30].strip()
                        user = line[30:42].strip()
                        state = line[43:48].strip()
                        started = line[49:68].strip()
                        queue_data = line[69:99].strip()
                        # jclass = line[100:128].strip()
                        proc = line[129:148].strip()

                        if name not in exclude:
                            self.qstat_viewlist.AppendItem([pid, state, name, user, queue_data, proc, started])

                # get message texts
                for x in self.log_data["PID List"]:
                    o_file = os.path.join(self.user_dir, 'ansysedt.o'+x)
                    if os.path.exists(o_file):
                        output_text = ''
                        with open(o_file, 'r') as fi:
                            for msgline in fi:
                                output_text += msgline
                            if output_text != '':
                                self.add_log_entry(x, 'Submit Message: ' + output_text, scheduler=True)
                        os.remove(o_file)

                    e_file = os.path.join(self.user_dir, 'ansysedt.e' + x)
                    if os.path.exists(e_file):
                        error_text = ''
                        with open(e_file, 'r') as fi:
                            for msgline in fi:
                                error_text += msgline
                            if error_text != '':
                                self.add_log_entry(x, 'Submit Error: ' + error_text, scheduler=True)
                        os.remove(e_file)
                counter = 0

            time.sleep(0.5)
            counter += 1

    def rmb_on_scheduler_msg_list(self, _unused):
        position = wx.ContextMenuEvent(type=wx.wxEVT_NULL)
        self.PopupMenu(ClearMsgPopupMenu(self), position.GetPosition())

    def leftclick_processtable(self, _unused):
        """On double click on process row will propose to abort running job"""
        row = self.qstat_viewlist.GetSelectedRow()
        pid = self.qstat_viewlist.GetTextValue(row, 0)
        queue_val = self.qstat_viewlist.GetTextValue(row, 4)

        result = add_message("Abort Queue Process {}?\n".format(pid), "Confirm Abort", "?")

        if result == wx.ID_OK:
            subprocess.call('qdel '+pid, shell=True)
            msg = "Job on {1} cancelled from GUI".format(pid, queue_val)
            try:
                self.log_data["PID List"].remove(pid)
            except ValueError:
                pass
            self.add_log_entry(pid, msg, scheduler=False)

    def select_queue(self, _unused):
        queue_value = self.queue_dropmenu.GetValue()
        init_combobox(queue_dict[queue_value]["parallel_env"], self.pe_dropmenu, queue_dict[queue_value]["default_pe"])
        self.select_pe(None)
        tst = node_config_str[queue_value]
        self.m_node_label.LabelText = tst

    def on_advanced_check(self, _unused):
        """callback called when clicked Advanced options"""
        if self.advanced_checkbox.Value:
            self.advanced_options_text.Show()
        else:
            self.advanced_options_text.Hide()

    def on_reserve_check(self, _unused):
        """callback called when clicked Reservation"""
        if self.reserved_checkbox.Value:
            self.reservation_id_text.Show()
        else:
            self.reservation_id_text.Hide()

    def click_launch(self, _unused):
        """Depending on the choice of the user invokes AEDT on visual node or simply for pre/post"""
        check_ssh()

        # Scheduler data
        scheduler = '/ott/apps/uge/bin/lx-amd64/qsub'
        queue_val = self.queue_dropmenu.Value
        penv = self.pe_dropmenu.Value
        num_cores = self.m_numcore.Value
        ver_str = self.m_select_version1.Value
        aedt_path = install_dir[ver_str]

        env = self.advanced_options_text.Value
        if self.env_var_text.Value:
            env += "," + self.env_var_text.Value

        # verify that no double commas, spaces, etc

        if env:
            env = re.sub(" ", "", env)
            env = re.sub(",+", ",", env)
            env = env.rstrip(",").lstrip(",")

        self.set_registry(aedt_path)
        self.usage_stat()

        op_mode = self.submit_mode_radiobox.GetSelection()
        if op_mode == 1:
            command = [scheduler, "-q", queue_val, "-pe", penv, num_cores]

            # if self.exclusive_usage_checkbox.Value:
            #     command += ["-l", "exclusive"]

            # Interactive mode
            command += ["-terse", "-v", env, "-b", "yes"]

            # insert job ID if provided. Should be always as first argument of qsub
            if self.reserved_checkbox.Value:
                ar = self.reservation_id_text.Value
                if ar in [None, ""]:
                    return add_message("Reservation ID is not provided. Please set ID and click launch again",
                                       "Reservation ID", "!")
                command[1:1] = ["-ar", ar]

            command += [os.path.join(aedt_path, "ansysedt"), "-machinelist", "num="+num_cores]

            res = subprocess.check_output(command, shell=False)
            pid = res.decode().strip()
            msg = "Job submitted to {0} on {1}\nSubmit Command:{2}".format(queue_val, scheduler, " ".join(command))
            self.add_log_entry(pid, msg, scheduler=False)
            self.log_data["PID List"].append(pid)

        else:
            threading.Thread(target=self._submit_batch_thread, daemon=True, args=(aedt_path, env,)).start()

    def usage_stat(self):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stat_file = os.path.join(self.user_dir, '.aedt', "run.log")
        with open(stat_file, "a") as file:
            file.write(self.m_select_version1.Value + "\t" + timestamp + "\n")

    def set_registry(self, aedt_path):
        if not os.path.isdir(self.path_textbox.Value):
            os.mkdir(self.path_textbox.Value)

        registry_file = os.path.join(aedt_path, "UpdateRegistry")
        # disable question about participation in product improvement
        command = ('{} -set -ProductName {} -RegistryKey ' +
                   '"Desktop/Settings/ProjectOptions/ProductImprovementOptStatus"' +
                   ' -RegistryValue 0 -RegistryLevel user').format(registry_file,
                                                                   self.products[self.m_select_version1.Value])
        subprocess.call([command], shell=True)

        # set installation path
        command = ('{0} -set -ProductName {1} -RegistryKey "Desktop/InstallationDirectory"' +
                   ' -RegistryValue {2} -RegistryLevel user').format(registry_file,
                                                                     self.products[self.m_select_version1.Value],
                                                                     aedt_path)
        subprocess.call([command], shell=True)

        # set project folder
        command = ('{0} -set -ProductName {1} -RegistryKey "Desktop/ProjectDirectory"' +
                   ' -RegistryValue {2} -RegistryLevel user').format(registry_file,
                                                                     self.products[self.m_select_version1.Value],
                                                                     self.path_textbox.Value)
        subprocess.call([command], shell=True)

        # disable welcome message
        command = ('{0} -set -ProductName {1} -RegistryKey "Desktop/Settings/ProjectOptions/ShowWelcomeMsg"' +
                   ' -RegistryValue 0 -RegistryLevel user').format(registry_file,
                                                                   self.products[self.m_select_version1.Value])
        subprocess.call([command], shell=True)

        # set personal lib
        command = ('{0} -set -ProductName {1} -RegistryKey "Desktop/PersonalLib" -RegistryValue ' +
                   '"$HOME/Ansoft/Personallib" -RegistryLevel user').format(registry_file,
                                                                            self.products[self.m_select_version1.Value])
        subprocess.call([command], shell=True)

        # set SGE scheduler
        command = '{} -set -ProductName {}  -FromFile "/ott/apps/software/AEDT_Launcher/sge_settings.areg"'.format(
                                                            registry_file, self.products[self.m_select_version1.Value])
        subprocess.call([command], shell=True)



    def m_update_msg_list(self, _unused):
        self.update_msg_list()

    def delete_row(self, _unused):
        """By clicking on Delete Row button delete row and rewrite json file with builds"""
        row = self.user_build_viewlist.GetSelectedRow()
        if row != -1:
            self.user_build_viewlist.DeleteItem(row)
            self.write_custom_build()

    def add_new_build(self, _unused):
        """By click on Add New Build opens file dialogue to select path and input box to set name.
        At the end we update JSON file with custom builds"""
        get_dir_dialogue = wx.DirDialog(None, "Choose a Linux64 directory:",
                                        style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if get_dir_dialogue.ShowModal() == wx.ID_OK:
            path = get_dir_dialogue.GetPath()
            get_dir_dialogue.Destroy()
        else:
            get_dir_dialogue.Destroy()
            return

        if "Linux64" not in path[-7:]:
            add_message("Your path should include and be ended by Linux64 (eg /ott/apps/ANSYSEM/Linux64)",
                             "Wrong path", "!")
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

    def set_project_path(self, _unused):
        get_dir_dialogue = wx.DirDialog(None, "Choose directory:", style=wx.DD_DEFAULT_STYLE)
        if get_dir_dialogue.ShowModal() == wx.ID_OK:
            path = get_dir_dialogue.GetPath()
            get_dir_dialogue.Destroy()
        else:
            get_dir_dialogue.Destroy()
            return

        self.path_textbox.Value = path

    def _shutdown_app(self, _unused):
        """Exit from app by clicking X or Close button. Kill the process to kill all child threads"""
        self.timer_stop()
        while len(threading.enumerate()) > 1:  # possible solution to wait until all threads are dead
            time.sleep(0.25)

        signal.pthread_kill(threading.get_ident(), signal.SIGINT)
        os.kill(os.getpid(), signal.SIGINT)

    @staticmethod
    def _submit_batch_thread(aedt_path, env):
        """
        Configure SGE scheduler.
        Viz-node for pre-post or submit. Command example:
        /bin/sh -c "export ANS_NODEPCHECK=1; export SKIP_MESHCHECK=0;
        /ott/apps/software/ANSYS_EM_2019R1/AnsysEM19.3/Linux64/ansysedt &"
        """

        # invoke electronics desktop
        shell = "/bin/sh -c "
        env_vars = ""
        if env:
            for variable in env.split(","):
                env_vars += 'export {}; '.format(variable)

        # command = command.replace(';"', '; export"')  # to print all exported variables
        command = '{} "{}{} &"'.format(shell, env_vars, os.path.join(aedt_path, "ansysedt"))
        subprocess.call([command], shell=True)


def check_ssh():
    """verify that all passwordless SSH are in place"""
    ssh_path = os.path.join(os.environ["HOME"], ".ssh")
    for file in ["authorized_keys", "config"]:
        if not os.path.isfile(os.path.join(ssh_path, file)):
            shutil.rmtree(ssh_path)
            proc = subprocess.Popen(["/nfs/ott/apps/admin/run_me_first.sh"], stdin=subprocess.PIPE, shell=True)
            proc.communicate(input=b"\n\n\n")
            break


def add_message(message, titel="", icon="?"):
    if icon == "?":
        icon = wx.OK | wx.CANCEL | wx.ICON_QUESTION
    elif icon == "!":
        icon = wx.OK | wx.ICON_ERROR
    else:
        icon = wx.OK | wx.ICON_INFORMATION

    dlg_qdel = wx.MessageDialog(None, message, titel, icon)
    result = dlg_qdel.ShowModal()
    dlg_qdel.Destroy()

    return result


def init_combobox(entry_list, combobox, default_value=''):
    """
    Fills a wx.Combobox lement with the entries in a list
    Input parameters
    :param entry_list: List of text entries to appear in the combobox element
    :param combobox: object pointing to the combobox element
    :param default_value: (optional9 default value (must be present in the entry list, otherwise will be ignored)

    Outputs
    :return: None
    """
    combobox.Clear()
    index = 0
    for i, v in enumerate(list(entry_list)):
        if v == default_value:
            index = i
        combobox.Append(v)
    combobox.SetSelection(index)


def main():
    """Main function to generate UI. Validate that only one instance is opened."""
    # this 0.7 sleep prevents double open if user has single click launch in Linux and performs double click
    time.sleep(0.7)

    app = wx.App()
    try:
        me = singleton.SingleInstance()  # should be assigned to "me", otherwise does not work
    except singleton.SingleInstanceException:
        add_message("Cannot open multiple instances. Close all launchers before you start new one",
                    "Instance error", "!")
        return

    ex = MyWindow(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
