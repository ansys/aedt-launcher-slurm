import os
import getpass
import socket
import errno
import json
import subprocess
import time
import threading
from datetime import datetime

#-----------------------------------------------------------------------------------------------------------------------
#  Imports & Dependencies
#-----------------------------------------------------------------------------------------------------------------------
import wx
import matplotlib
from src_gui import GUIFrame

matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
#from matplotlib.backends.backend_wx import NavigationToolbar2Wx
#from matplotlib.figure import Figure
import matplotlib.pyplot as plt
#-----------------------------------------------------------------------------------------------------------------------
#  Perhaps save user settings ?
#-----------------------------------------------------------------------------------------------------------------------
# For each user there could be a config file with settings. Otherwise use defaults

#-----------------------------------------------------------------------------------------------------------------------
# Simple dictionary for the versions (* at the beginning) for the default version
default_version = u"2019 R1"
install_dir = {
# -----------------------------------------------------------------------------------------------------------------------
    u"R18.2":   '/ott/apps/software/ANSYS_EM_182/AnsysEM18.2/Linux64/ansysedt',
    u"R19.0":   '/ott/apps/software/ANSYS_EM_190/AnsysEM19.0/Linux64/ansysedt',
    u"R19.1":   '/ott/apps/software/ANSYS_EM_191/AnsysEM19.1/Linux64/ansysedt',
    u"R19.2":   '/ott/apps/software/ANSYS_EM_192/AnsysEM19.2/Linux64/ansysedt',
    u"2019 R1": '/ott/apps/software/ANSYS_EM_2019R1/AnsysEM19.3/Linux64/ansysedt',
    u"2019 R2 Certified 28.02.2019":  '/ott/apps/daily_builds/linx64/v194_EBU_280219/AnsysEM19.4/Linux64/ansysedt'
}


#-----------------------------------------------------------------------------------------------------------------------
# Define Available Queues
#-----------------------------------------------------------------------------------------------------------------------
class queue_data:
    def __init__(self, num_cores, avail_cores, cores_per_node, mem_per_node, parallel_env, default_pe):
        self.num_cores = num_cores
        self.avail_cores = avail_cores
        self.cores_per_node = cores_per_node
        self.mem_per_node = mem_per_node
        self.parallel_env = parallel_env
        self.default_pe = default_pe

default_queue = u'euc09'

queue = {
    u'euc09':    queue_data(0, 0, 20,'128GB', ['pe_mpi_te', 'electronics-8', 'electronics-16', 'electronics-20'], 'electronics-8'),
    u'ottc01' :  queue_data(0, 0, 28,'128GB', ['pe_mpi_te', 'electronics-8', 'electronics-16', 'electronics-28'], 'electronics-8'),
    u'euc09lm':  queue_data(0, 0, 28,'512GB', ['pe_mpi_te', 'electronics-8', 'electronics-16', 'electronics-28'], 'electronics-8')
}

#-----------------------------------------------------------------------------------------------------------------------
# Define default number of cores for the selected PE (interactive mode)
#-----------------------------------------------------------------------------------------------------------------------
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


# Benutzerenv.
# Launcher GUI vorhanden
# settings koennen gespeichert werden (evtl.)
# SGE Scheduler setup per default

# Nice Grid Engine infos
# https://idos-wiki.unibe.ch/demo/beispiel-dokumentation/interacting-with-the-grid-engine
# Comments on parallel-environment
# pe_mpi_ti hat tight integration, d.h. der Scheduler uebernimmt die Kontrolle der slaves und eine andere
# allocation rule. Bei electronics-28 ist diese "fix" auf 28 cores eingestellt, bei pe_mpi_ti auf $fill_up
# bei nicht exklusiver Nutzung fuellt der Scheduler die Nodes bis zum Maximum

#-----------------------------------------------------------------------------------------------------------------------
# At start - get cluster data and store accordingly
#-----------------------------------------------------------------------------------------------------------------------

class CreatePlot(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        used = []
        rest = []
        xes = []
        for queue_name in queue:
            tpl = queue[queue_name]
            num_nodes = str(int(tpl.num_cores / tpl.cores_per_node))
            available = float(tpl.avail_cores)/float(tpl.num_cores)*100.0
            used_cpu = 100-available
            used.append(used_cpu)
            rest.append(available)
            xes.append(queue_name+': '+num_nodes+' Nodes\n'+str(tpl.cores_per_node)+' cores/node '+str(tpl.mem_per_node))

        ind = xes  # the x locations for the groups
        width = 0.35  # the width of the bars: can also be len(x) sequence
        p1 = plt.bar(ind, used, width, color='r')
        p2 = plt.bar(ind, rest, width, bottom=used, color='g')

        plt.ylabel('Loading [%]')
        plt.title('Queue Loading Summary')

        # Define x axis as the discreate queue names
        nq = len(queue)
        plt.xticks(range(0,nq), ind)
        plt.margins(0.02, 0.1)

        # Define the y axis as a percent of total loading (25% ticks)
        dp = 25
        yrange = range(0, 100+dp, dp)
        plt.yticks(yrange, [ str(i)+'%' for i in yrange ])
        self.figure = plt.gcf()

        self.canvas = FigureCanvas(parent, -1, self.figure)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.TOP | wx.LEFT | wx.EXPAND)
        parent.SetSizer(sizer)
        parent.Fit()

class MyWindow( GUIFrame ):

    # === INITIALIZATION =================================================================================
    def __init__(self, parent):
        # Initialize the main form
        GUIFrame.__init__(self, parent)

        # -------------------------------------------------------------------------------------------------------------------
        # Get environment data
        # -------------------------------------------------------------------------------------------------------------------
        self.user_dir = os.path.expanduser('~')
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.display_node = os.getenv('DISPLAY')
        self.console_text = ""
        self.shutdown = False
        self.t = None

        if self.display_node[0] == ':':
            self.display_node = self.hostname + self.display_node

        vnc_nodes = ['ottvnc']
        dcv_nodes = ['eurgs']
        viz_type =  None
        for x in vnc_nodes:
            if x in self.display_node:
                viz_type = 'VNC'
                break
        if viz_type is None:
            for x in dcv_nodes:
                if x in self.display_node:
                    viz_type = 'DCV'
                    break

        MSG =  'No Status Message'
        if viz_type is None:
            MSG = "Warning: Unknown Display Type!!"
            viz_type = ''

        self.qsuboutput = os.path.join(self.user_dir, '.aedt', 'qsub_log')

        self.qstatdata = os.path.join(self.user_dir, '.aedt', 'cluster_usage')
        if not os.path.exists(os.path.dirname(self.qstatdata)):
            try:
                os.makedirs(os.path.dirname(self.qstatdata))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        self.qstat = "/ott/apps/uge/bin/lx-amd64/qstat"
        subprocess.call(self.qstat + ' -g c > ' + self.qstatdata, shell=True)

        '''
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
        '''
        try:
            # also define working directory based on user home directory
            with open(self.qstatdata) as f:
                for line in f:
                    data = line.split()
                    queue_name = data[0]
                    if queue_name in queue:
                        tpl = queue[queue_name]
                        tpl.num_cores = int(data[5])
                        tpl.avail_cores = int(data[4])

        except Exception as e:
            pass

        # -------------------------------------------------------------------------------------------------------------------
        # Set the status bars
        # -------------------------------------------------------------------------------------------------------------------
        self.m_statusBar1.SetStatusText('User: ' + self.username + ' on ' + viz_type + ' node ' + self.display_node , 0)
        self.m_statusBar1.SetStatusText(MSG, 1)
        self.m_statusBar1.SetStatusWidths([500, -1])

        # -------------------------------------------------------------------------------------------------------------------
        #  Initialize the comboboxes:
        #    AEDT Version
        #    Queue
        #    Parallel Environment
        # -------------------------------------------------------------------------------------------------------------------
        # Add the custom build directories to the standard paths
        # Define column names of table
        self.m_grid2.SetColLabelValue(0, "Label")
        self.m_grid2.SetColLabelValue(1, "Executable")
        # load rows of builds
        self.userbuildfile = os.path.join(self.user_dir, '.aedt', 'user_build.json')
        if os.path.exists(self.userbuildfile):
            with open(self.userbuildfile,'r') as fi:
                self.userbuild = json.load(fi)
                count =  0
                for key, val in self.userbuild.items():
                    self.m_grid2.AppendRows(1)
                    self.m_grid2.SetCellValue(count,0,key)
                    self.m_grid2.SetCellValue(count, 1, val)
                    install_dir[key]=val
                    count += 1

        # Update

        init_combobox(install_dir.keys(), self.m_select_version1, default_version)
        init_combobox(queue.keys(), self.m_select_queue, default_queue)




        self.interactive_env = ",".join(["DISPLAY=" + self.display_node, "LIBGL_ALWAYS_INDIRECT=True",
                                    "LIBGL_ALWAYS_SOFTWARE=True", "GALLIUM_DRIVER=swr", "ANS_NODEPCHECK=1"])

        self.m_OptionsText.Value = self.interactive_env

        self.local_env = ""

        self.m_select_queue.Value = default_queue
        self.select_queue(None)


        # Create chart
        self.sizer = self.page_Data.GetSizer()
        self.plot_container = self.page_Data
        self.plotpanel = CreatePlot(self.plot_container)

        # Setup Process Log
        self.m_dataViewListCtrl2.AppendTextColumn('Timestamp', width=140)
        self.m_dataViewListCtrl2.AppendTextColumn('PID', width=50)
        self.m_dataViewListCtrl2.AppendTextColumn('Message', width=400)
        self.logfile = os.path.join(self.user_dir, '.aedt', 'user_log_'+viz_type+'.json')

        # read in previous log file
        if os.path.exists(self.logfile):
            with open (self.logfile, 'r') as fi:
                self.log_data = json.load(fi)
                self.update_msg_list()
        else:
            self.log_data = {"Message List": [],
                             "PID List": [],
                             "GUI Data": []}

        # Setup Process List
        self.m_dataViewListCtrl1.AppendTextColumn('PID', width=50)
        self.m_dataViewListCtrl1.AppendTextColumn('State', width=50)
        self.m_dataViewListCtrl1.AppendTextColumn('Name', width=80)
        self.m_dataViewListCtrl1.AppendTextColumn('User', width=50)
        self.m_dataViewListCtrl1.AppendTextColumn('Queue', width=200)
        self.m_dataViewListCtrl1.AppendTextColumn('cpu', width=30)
        self.m_dataViewListCtrl1.AppendTextColumn('Started', width=50)
        self.running = True
        threading.Thread(target=self.update_process_list, daemon=True).start()
        pass

        # Disable Batch-mode radio button
        self.m_radioBox1.EnableItem(1,False)
        if viz_type == 'DCV':
            self.m_radioBox1.EnableItem(2,False)
            self.m_radioBox1.Select(0)
        else:
            self.m_radioBox1.EnableItem(2, True)
            self.m_radioBox1.Select(2)

        self.select_mode(None)

        self.m_notebook2.ChangeSelection(0)


    def timer_stop(self):
        self.running = False
        pass

    def select_pe(self, event):
        ''' Callback for the selection of parallel environment. Primarily used to set an appropriate number of cores'''
        pe_val = self.m_select_pe.Value
        core_val = pe_cores[pe_val]
        self.m_numcore.Value = str(core_val)
        pass

    def select_mode(self, event):
        modes = self.m_radioBox1.Strings
        sel = self.m_radioBox1.Selection
        if sel == 0 or sel == 1:
            self.m_select_queue.Enabled = False
            self.m_numcore.Enabled = False
            self.m_checkBox2.Enabled = False
            self.m_node_label.Enabled = False
            self.m_select_pe.Enable(False)
            self.m_OptionsText.Value= self.local_env
            pass
        else:
            # Interactive model: set default to 8 cores
            self.m_select_queue.Enabled = True
            self.m_numcore.Enabled = True
            self.m_checkBox2.Enabled = True
            self.m_node_label.Enabled = True
            self.m_OptionsText.Value
            self.m_select_pe.Enable(True)
            self.m_OptionsText.Value = self.interactive_env
            pass

    def update_msg_list(self):
        try:
            self.m_dataViewListCtrl2.DeleteAllItems()
        except:
            return False

        for msg in self.log_data["Message List"]:
            sched = msg[3]
            if sched or self.m_checkBox_allmsg.Value:
                tab_data = msg[0:3]
                self.m_dataViewListCtrl2.PrependItem(tab_data)

    def add_log_entry(self, pid, msg, scheduler=False):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = [timestamp, pid, msg, scheduler]
        if scheduler or self.m_checkBox_allmsg.Value:
            tab_data = data[0:3]
            self.m_dataViewListCtrl2.PrependItem(tab_data)
        self.log_data["Message List"].append(data)
        with open(self.logfile, 'w') as fa:
            json.dump(self.log_data, fa)

    def submit_batch_thread(self):  # viz-node for pre-post or submit
        command = [self.aedt_ver + '&']
        subprocess.call(command, shell=True)

    def update_process_list(self):
        while self.running:
            subprocess.call(self.qstat + ' > ' + self.qstatdata, shell=True)
            try:
                self.m_dataViewListCtrl1.DeleteAllItems()
            except:
                return False
            process_list = {}
            message_list = {}
            exclude = ['VNC Deskto', 'DCV Deskto']
            with open(self.qstatdata) as f:
                for i, line in enumerate(f):
                    if i > 1:
                        PID = line[0:10].strip()
                        prior = line[11:18].strip()
                        name = line[19:30].strip()
                        user = line[30:42].strip()
                        state = line[43:48].strip()
                        started = line[49:68].strip()
                        queue = line[69:99].strip()
                        jclass = line[100:128].strip()
                        proc = line[129:148].strip()

                        if name not in exclude:
                            self.m_dataViewListCtrl1.AppendItem([PID, state, name, user, queue, proc, started])

                    pass
            pass

            # get message texts
            for x in self.log_data["PID List"]:
                o_file = os.path.join(self.user_dir, 'ansysedt.o'+x)
                if os.path.exists(o_file):
                    output_text = ''
                    with open(o_file,'r') as fi:
                        for msgline in fi:
                            output_text += msgline
                        if output_text != '':
                            self.add_log_entry(x, 'Submit Message: ' + output_text, scheduler=True)
                    os.remove(o_file)

                e_file = os.path.join(self.user_dir, 'ansysedt.e' + x)
                if os.path.exists(e_file):
                    error_text = ''
                    with open(e_file,'r') as fi:
                        for msgline in fi:
                            error_text += msgline
                        if error_text != '':
                            self.add_log_entry(x, 'Submit Error: ' + error_text, scheduler=True)
                    os.remove(e_file)
            time.sleep(3)
            pass
        else:
            self.Close()

    def leftclick_processtable(self, event):
        row = self.m_dataViewListCtrl1.GetSelectedRow()
        pid = self.m_dataViewListCtrl1.GetTextValue(row,0)
        queue = self.m_dataViewListCtrl1.GetTextValue(row, 4)

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

    def m_check_edit(self, event):
        if self.m_checkBox1.Value:
            self.m_OptionsText.Enabled = True
        else:
            self.m_OptionsText.Enabled = False

    def select_queue(self, event):
        val = self.m_select_queue.GetValue()
        init_combobox(queue[val].parallel_env, self.m_select_pe, queue[val].default_pe)
        self.select_pe(None)
        tst = node_config_str[val]
        self.m_node_label.LabelText = tst
        pass


    def click_launch(self, event):
        # Scheduler data
        scheduler = '/ott/apps/uge/bin/lx-amd64/qsub'
        queue = self.m_select_queue.Value
        penv = self.m_select_pe.Value
        num_cores = self.m_numcore.Value
        ver_str = self.m_select_version1.Value

        self.aedt_ver=install_dir[ver_str]

        env = self.m_OptionsText.Value
        op_mode = self.m_radioBox1.GetSelection()

        self.console = os.path.join(self.user_dir, '.aedt', 'console')

        if op_mode == 2:

            # Interactive mode
            command = [ scheduler, "-q", queue, "-pe", penv, num_cores, "-terse", "-v", env, "-b", "yes", self.aedt_ver, "-machinelist", "num="+num_cores]
            sh = False
            res = subprocess.check_output(command, shell=sh)
            pid = res.decode().strip()
            msg = "Job submitted to {0} on {1}\n{2}".format(queue, scheduler, " ".join(command))
            self.add_log_entry(pid, msg, scheduler=False)
            self.log_data["PID List"].append(pid)
        else:
            threading.Thread(target=self.submit_batch_thread, daemon=True).start()
        pass

    def click_cancel(self, event):
        self.shutdown_app(None)

    def shutdown_app(self, event):
        self.Destroy()

    def m_update_msg_list(self, event):
        self.update_msg_list()

    def delete_row(self, event):
        a = self.m_grid2.GetSelectedRows()
        for x in a:
            label = self.m_grid2.GetCellValue(x, 0)
            self.m_grid2.DeleteRows(x)
            self.userbuild.pop(label, None)

        self.m_grid2.ForceRefresh()

        with open(self.userbuildfile, 'w') as fo:
            json.dump(self.userbuild, fo)

    def add_row(self, event):
        self.m_grid2.ClearSelection()
        self.m_grid2.AppendRows(1)
        self.m_grid2.ForceRefresh()
        pass

    def edit_cell(self, event):
        color = (255, 255, 153)
        white = (255, 255, 255)
        valid = False
        row = event.GetRow()
        b = event.GetCol()
        label = self.m_grid2.GetCellValue(row, 0)
        exe = self.m_grid2.GetCellValue(row, 1)
        if label != '':
            if os.path.isfile(exe):
                self.m_grid2.SetCellBackgroundColour(row, 0, white)
                self.m_grid2.SetCellBackgroundColour(row, 1, white)
                valid = True
                pass  # update builds list
            else:
                self.m_grid2.SetCellBackgroundColour(row,1, color)
        else:
            self.m_grid2.SetCellValue(row, 0, "<Enter Label>")
            self.m_grid2.SetCellBackgroundColour(row, 0, color )
        if valid:
            try:
                self.userbuild[label] = exe
            except:
                self.userbuild = {label: exe}
            with open(self.userbuildfile,'w') as fo:
                json.dump(self.userbuild, fo)


def init_combobox(entry_list, c_box, default_value=''):
    '''
    Fills a wx.Combobox lement with the entries in a list
    Input parameters
    :param entry_list: List of text entries to appear in the combobox element
    :param c_box: object pointing to the combobox element
    :param default_value: (optional9 default value (must be present in the entry list, otherwise will be ignored)

    Outputs
    :return: None
    '''
    values = sorted(entry_list)
    c_box.Clear()
    index = 0
    for i,v in enumerate(values):
        if v == default_value:
            index = i
        c_box.Append(v)
    c_box.SetSelection(index)



def main():

    app = wx.App()
    ex = MyWindow(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()