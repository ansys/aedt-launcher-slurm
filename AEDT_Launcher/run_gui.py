from src_gui import GUIFrame
from datetime import datetime

import os
import getpass
import socket
import errno
import json
import subprocess
import time
import threading
import wx
# matplotlib import block should be together
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import matplotlib.pyplot as plt

#  Perhaps save user settings ?
# For each user there could be a config file with settings. Otherwise use defaults


# Simple dictionary for the versions (* at the beginning) for the default version
default_version = u"2019 R1"
install_dir = {

    u"R18.2":   '/ott/apps/software/ANSYS_EM_182/AnsysEM18.2/Linux64/ansysedt',
    u"R19.0":   '/ott/apps/software/ANSYS_EM_190/AnsysEM19.0/Linux64/ansysedt',
    u"R19.1":   '/ott/apps/software/ANSYS_EM_191/AnsysEM19.1/Linux64/ansysedt',
    u"R19.2":   '/ott/apps/software/ANSYS_EM_192/AnsysEM19.2/Linux64/ansysedt',
    u"2019 R1": '/ott/apps/software/ANSYS_EM_2019R1/AnsysEM19.3/Linux64/ansysedt',
    u"2019 R2":  '/ott/apps/software/ANSYS_EM_2019R2/AnsysEM19.4/Linux64/ansysedt'
}


# Define Available Queues
class QueueData:
    def __init__(self, num_cores, avail_cores, cores_per_node, mem_per_node, parallel_env, default_pe):
        self.num_cores = num_cores
        self.avail_cores = avail_cores
        self.cores_per_node = cores_per_node
        self.mem_per_node = mem_per_node
        self.parallel_env = parallel_env
        self.default_pe = default_pe

    def num_nodes(self):
        return str(int(self.num_cores / self.cores_per_node))

    def available(self):
        return float(self.avail_cores) / float(self.num_cores) * 100.0

    def used_cpu(self):
        return 100 - self.available()


default_queue = u'euc09'
queue = {
    u'euc09': QueueData(0, 0, 20, '128GB',
                        ['pe_mpi_te', 'electronics-8', 'electronics-16', 'electronics-20'], 'electronics-8'),
    u'ottc01': QueueData(0, 0, 28, '128GB',
                         ['pe_mpi_te', 'electronics-8', 'electronics-16', 'electronics-28'], 'electronics-8'),
    u'euc09lm': QueueData(0, 0, 28, '512GB',
                          ['pe_mpi_te', 'electronics-8', 'electronics-16', 'electronics-28'], 'electronics-8')
}

# Define default number of cores for the selected PE (interactive mode)
pe_cores = {
    'pe_mpi_te':        4,
    'electronics-8':    8,
    'electronics-16':   16,
    'electronics-20':   20,
    'electronics-28':   28
}
node_config_str = {
    'euc09':    '(20 cores, 128GB  / node)',
    'ottc01':   '(28 cores, 128GB  / node)',
    'euc09lm':  '(28 cores, 512GB  / node)'
}


# Nice Grid Engine infos
# https://idos-wiki.unibe.ch/demo/beispiel-dokumentation/interacting-with-the-grid-engine
# Comments on parallel-environment
# pe_mpi_ti hat tight integration, d.h. der Scheduler uebernimmt die Kontrolle der slaves und eine andere
# allocation rule. Bei electronics-28 ist diese "fix" auf 28 cores eingestellt, bei pe_mpi_ti auf $fill_up
# bei nicht exklusiver Nutzung fuellt der Scheduler die Nodes bis zum Maximum


# At start - get cluster data and store accordingly
class CreatePlot(wx.Panel):
    def __init__(self, parent):
        self.parent = parent
        wx.Panel.__init__(self, parent, -1)
        self.update_plot()

    def update_plot(self):
        used = []
        rest = []
        xes = []
        for queue_name in queue:
            queue_data = queue[queue_name]
            used.append(queue_data.used_cpu())
            rest.append(queue_data.available())
            xes.append('{}: {} Nodes\n{} cores/node {}\nFree cores: {}/{}'.format(queue_name, queue_data.num_nodes(),
                                                               queue_data.cores_per_node,
                                                               queue_data.mem_per_node,
                                                               queue_data.avail_cores, queue_data.num_cores))

        plt.clf()  # clear the plot to create a new one to update cluster usage
        width = 0.35  # the width of the bars: can also be len(x) sequence
        plt.bar(xes, used, width, color='r')
        plt.bar(xes, rest, width, bottom=used, color='g')

        plt.ylabel('Loading [%]')
        plt.title('Queue Loading Summary')

        # Define x axis as the discreate queue names
        nq = len(queue)
        plt.xticks(range(0, nq), xes)
        plt.margins(0.02, 0.1)

        # Define the y axis as a percent of total loading (20% ticks)
        dp = 20
        yrange = range(0, 100+dp, dp)
        plt.yticks(yrange, [str(i)+'%' for i in yrange])
        self.figure = plt.gcf()

        self.canvas = FigureCanvas(self.parent, -1, self.figure)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.TOP | wx.LEFT | wx.EXPAND)
        self.parent.SetSizer(sizer)
        self.parent.Fit()


class ClearMsgPopupMenu(wx.Menu):

    def __init__(self, parent):
        super(ClearMsgPopupMenu, self).__init__()

        self.parent = parent

        mmi = wx.MenuItem(self, wx.NewId(), 'Clear All Messages')
        self.Append(mmi)
        self.Bind(wx.EVT_MENU, self.on_clear, mmi)

    def on_clear(self, e):
        self.parent.scheduler_msg_viewlist.DeleteAllItems()
        self.parent.log_data = {"Message List": [],
                                "PID List": [],
                                "GUI Data": []}

        if os.path.isfile(self.parent.logfile):
            os.remove(self.parent.logfile)


class MyWindow(GUIFrame):
    def __init__(self, parent):
        # Initialize the main form
        GUIFrame.__init__(self, parent)

        # Get environment data
        self.user_dir = os.path.expanduser('~')
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.display_node = os.getenv('DISPLAY')

        # get paths
        self.qsuboutput = os.path.join(self.user_dir, '.aedt', 'qsub_log')
        self.qstat_cluster = os.path.join(self.user_dir, '.aedt', 'cluster_usage')
        self.qstat_user = os.path.join(self.user_dir, '.aedt', 'user_usage')
        self.user_build_json = os.path.join(self.user_dir, '.aedt', 'user_build.json')
        self.builds_data = {}

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

        if not os.path.exists(os.path.dirname(self.qstat_cluster)):
            try:
                os.makedirs(os.path.dirname(self.qstat_cluster))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        self.qstat = "/ott/apps/uge/bin/lx-amd64/qstat"
        subprocess.call(self.qstat + ' -g c > ' + self.qstat_cluster, shell=True)

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
        try:
            # also define working directory based on user home directory
            with open(self.qstat_cluster) as f:
                for line in f:
                    data = line.split()
                    queue_name = data[0]
                    if queue_name in queue:
                        queue_data = queue[queue_name]
                        queue_data.num_cores = int(data[5])
                        queue_data.avail_cores = int(data[4])

        except Exception as e:
            pass

        # Set the status bars on the bottom of the window
        self.m_statusBar1.SetStatusText('User: ' + self.username + ' on ' + viz_type + ' node ' + self.display_node, 0)
        self.m_statusBar1.SetStatusText(msg, 1)
        self.m_statusBar1.SetStatusWidths([500, -1])

        # create a list of default environmental variables
        init_combobox(install_dir.keys(), self.m_select_version1, default_version)
        init_combobox(queue.keys(), self.m_select_queue, default_queue)

        self.interactive_env = ",".join(["DISPLAY=" + self.display_node, "LIBGL_ALWAYS_INDIRECT=True",
                                         "LIBGL_ALWAYS_SOFTWARE=True", "GALLIUM_DRIVER=swr", "ANS_NODEPCHECK=1"])

        self.advanced_options_text.Value = self.interactive_env

        self.local_env = "ANS_NODEPCHECK=1"

        self.m_select_queue.Value = default_queue
        self.select_queue(None)

        # Create chart
        self.sizer = self.page_Data.GetSizer()
        self.plot_container = self.page_Data
        self.plotpanel = CreatePlot(self.plot_container)

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
        self.running = True

        # run in parallel to UI regular update of chart and process list
        threading.Thread(target=self.update_process_list, daemon=True).start()
        threading.Thread(target=self.update_cluster_load, daemon=True).start()

        # Disable Batch-mode radio button
        self.submit_mode_radiobox.EnableItem(1, False)
        if viz_type == 'DCV':
            self.submit_mode_radiobox.EnableItem(2, False)
            self.submit_mode_radiobox.Select(0)
        else:
            self.submit_mode_radiobox.EnableItem(2, True)
            self.submit_mode_radiobox.Select(2)

        self.select_mode(None)
        self.m_notebook2.ChangeSelection(0)
        self.advanced_options_text.Hide()  # hide on start since hidden attribute is not working in wxBuilder
        self.read_custom_builds()

    def read_custom_builds(self):
        """Reads all specified in JSON file custom builds"""
        if os.path.isfile(self.user_build_json):
            with open(self.user_build_json) as file:
                self.builds_data = json.load(file)

            for key in self.builds_data.keys():
                self.user_build_viewlist.AppendItem([key, self.builds_data[key]])

                # update values in version selector on 1st page
            init_combobox(list(self.builds_data.keys()) + list(install_dir.keys()), self.m_select_version1,
                          default_version)

    def write_custom_build(self):
        """Function to create a user JSON file with custom builds and to update selector"""
        num_rows = self.user_build_viewlist.GetItemCount()
        self.builds_data = {}

        for i in range(num_rows):
            self.builds_data[self.user_build_viewlist.GetTextValue(i, 0)] = self.user_build_viewlist.GetTextValue(i, 1)

        # update values in version selector on 1st page
        init_combobox(list(self.builds_data.keys()) + list(install_dir.keys()), self.m_select_version1, default_version)

        with open(self.user_build_json, "w") as file:
            json.dump(self.builds_data, file)

    def timer_stop(self):
        self.running = False

    def select_pe(self, event):
        """ Callback for the selection of parallel environment. Primarily used to set an appropriate number of cores"""
        pe_val = self.m_select_pe.Value
        core_val = pe_cores[pe_val]
        self.m_numcore.Value = str(core_val)

    def select_mode(self, event):
        """Callback invoked on change of the mode Pre/Post or Interactive"""
        sel = self.submit_mode_radiobox.Selection
        if sel == 0 or sel == 1:
            self.m_select_queue.Enabled = False
            self.m_numcore.Enabled = False
            self.exclusive_usage_checkbox.Enabled = False
            self.m_node_label.Enabled = False
            self.m_select_pe.Enable(False)
            self.advanced_options_text.Value = self.local_env
        else:
            # Interactive model: set default to 8 cores
            self.m_select_queue.Enabled = True
            self.m_numcore.Enabled = True
            self.exclusive_usage_checkbox.Enabled = True
            self.m_node_label.Enabled = True
            self.m_select_pe.Enable(True)
            self.advanced_options_text.Value = self.interactive_env

    def update_msg_list(self):
        try:
            self.scheduler_msg_viewlist.DeleteAllItems()
        except:
            return False

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

    def submit_batch_thread(self):  # viz-node for pre-post or submit
        command = [self.aedt_ver + '&']
        subprocess.call(command, shell=True)

    def update_cluster_load(self):
        """Update cluster load every 5s"""
        time.sleep(5)  # this sleep is preventing disappearing of a Plot due to threading
        while self.running:
            subprocess.call(self.qstat + ' -g c > ' + self.qstat_cluster, shell=True)
            try:
                # also define working directory based on user home directory
                with open(self.qstat_cluster) as f:
                    for line in f:
                        data = line.split()
                        queue_name = data[0]
                        if queue_name in queue:
                            queue_data = queue[queue_name]
                            queue_data.num_cores = int(data[5])
                            queue_data.avail_cores = int(data[4])

            except Exception as e:
                pass

            self.plotpanel.update_plot()
            time.sleep(5)

    def update_process_list(self):
        """Update a list of jobs status for a user every 3s"""
        while self.running:
            subprocess.call(self.qstat + ' > ' + self.qstat_user, shell=True)
            try:
                self.qstat_viewlist.DeleteAllItems()
            except:
                return False
            # process_list = {}
            # message_list = {}
            exclude = ['VNC Deskto', 'DCV Deskto']
            with open(self.qstat_user) as f:
                for i, line in enumerate(f):
                    if i > 1:
                        PID = line[0:10].strip()
                        # prior = line[11:18].strip()
                        name = line[19:30].strip()
                        user = line[30:42].strip()
                        state = line[43:48].strip()
                        started = line[49:68].strip()
                        queue = line[69:99].strip()
                        # jclass = line[100:128].strip()
                        proc = line[129:148].strip()

                        if name not in exclude:
                            self.qstat_viewlist.AppendItem([PID, state, name, user, queue, proc, started])

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
            time.sleep(3)
        else:
            self.Close()

    def rmb_on_scheduler_msg_list(self, event):
        position = wx.ContextMenuEvent(type=wx.wxEVT_NULL)
        self.PopupMenu(ClearMsgPopupMenu(self), position.GetPosition())

    def leftclick_processtable(self, event):
        """On double click on process row will propose to abort running job"""
        row = self.qstat_viewlist.GetSelectedRow()
        pid = self.qstat_viewlist.GetTextValue(row, 0)
        queue = self.qstat_viewlist.GetTextValue(row, 4)

        dlg_qdel = wx.MessageDialog(self,
                                    "Abort Queue Process ?\n",
                                    "Confirm Abort", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg_qdel.ShowModal()
        dlg_qdel.Destroy()

        if result == wx.ID_OK:
            subprocess.call('qdel '+pid, shell=True)
            msg = "Job on {1} cancelled from GUI".format(pid, queue)
            try:
                self.log_data["PID List"].remove(pid)
            except:
                pass
            self.add_log_entry(pid, msg, scheduler=False)

    def select_queue(self, event):
        val = self.m_select_queue.GetValue()
        init_combobox(queue[val].parallel_env, self.m_select_pe, queue[val].default_pe)
        self.select_pe(None)
        tst = node_config_str[val]
        self.m_node_label.LabelText = tst

    def on_advanced_check(self, event):
        """callback called when clicked Advanced options"""
        if self.advanced_checkbox.Value:
            self.advanced_options_text.Show()
        else:
            self.advanced_options_text.Hide()


    def click_launch(self, event):
        # Scheduler data
        scheduler = '/ott/apps/uge/bin/lx-amd64/qsub'
        queue = self.m_select_queue.Value
        penv = self.m_select_pe.Value
        num_cores = self.m_numcore.Value
        ver_str = self.m_select_version1.Value

        self.aedt_ver = install_dir[ver_str]

        env = self.advanced_options_text.Value
        if self.env_var_text.Value:
            env += "," + self.env_var_text.Value

        # verify that no double commas, spaces, etc
        env.rstrip()
        while ",," in env:
            env = env.replace(",,", ",")

        if env[-1] == ",":
            env = env[:-1]

        op_mode = self.submit_mode_radiobox.GetSelection()

        self.console = os.path.join(self.user_dir, '.aedt', 'console')

        if op_mode == 2:

            command = [scheduler, "-q", queue, "-pe", penv, num_cores]

            if self.exclusive_usage_checkbox.Value:
                command += ["-l", "exclusive" ]

            # Interactive mode
            command +=  ["-terse", "-v", env, "-b", "yes"]
            command +=  [self.aedt_ver, "-machinelist", "num="+num_cores]


            sh = False
            res = subprocess.check_output(command, shell=sh)
            pid = res.decode().strip()
            msg = "Job submitted to {0} on {1}\n{2}".format(queue, scheduler, " ".join(command))
            self.add_log_entry(pid, msg, scheduler=False)
            self.log_data["PID List"].append(pid)
        else:
            threading.Thread(target=self.submit_batch_thread, daemon=True).start()

    def click_close(self, event):
        """on click on Close button. Should invoke separate function to close window"""
        self.shutdown_app()

    def shutdown_app(self):
        """Exit from app"""
        self.Destroy()

    def m_update_msg_list(self, event):
        self.update_msg_list()

    def delete_row(self, event):
        row = self.user_build_viewlist.GetSelectedRow()
        if row != -1:
            self.user_build_viewlist.DeleteItem(row)
            self.write_custom_build()

    def add_new_build(self, event):
        """By click on Add New Build opens file dialogue to select path and input box to set name"""
        get_dir_dialogue = wx.DirDialog(None, "Choose a Linux64 directory:",
                                        style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if get_dir_dialogue.ShowModal() == wx.ID_OK:
            path = get_dir_dialogue.GetPath()
            get_dir_dialogue.Destroy()
        else:
            get_dir_dialogue.Destroy()
            return

        if "Linux64" not in path[-7:]:
            dlg = wx.MessageDialog(self,
                                    "Your path should include and be ended by Linux64 (eg /ott/apps/ANSYSEM/Linux64)",
                                    "Wrong path", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        get_name_dialogue = wx.TextEntryDialog(None, "Set name of a build:", value="AEDT_2019R3")
        if get_name_dialogue.ShowModal() == wx.ID_OK:
            name = get_name_dialogue.GetValue()
            get_name_dialogue.Destroy()
        else:
            get_name_dialogue.Destroy()
            return

        if name in [None, ""] + list(self.builds_data.keys()):
            dlg = wx.MessageDialog(self,
                                    "Name cannot be empty and not unique",
                                    "Wrong name", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # if all is fine add new build
        self.user_build_viewlist.AppendItem([name, path])
        self.write_custom_build()


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
    values = sorted(entry_list)
    combobox.Clear()
    index = 0
    for i, v in enumerate(values):
        if v == default_value:
            index = i
        combobox.Append(v)
    combobox.SetSelection(index)


def main():
    app = wx.App()
    ex = MyWindow(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
