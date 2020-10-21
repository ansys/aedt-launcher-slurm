## Description
Project aims to create a user friendly interface to submit interactive Electronics Desktop jobs in Linux environment.
Interactivee job means that the job will be submitted to the compute node using scheduling system (SGE) and will send
back Display to VNC session. This will allow user to run heavy projects on powerful machines and interact with design.

## Configuration
In order to run AEDT Launcher on your cluster you need to perform following steps:
1. pull current repository in your installation/app folder
2. copy [cluster_configuration.json](AEDT_Launcher/templates/cluster_configuration.json) to the same direction as 
[run_gui.py](AEDT_Launcher/run_gui.py) and modify the file according to your cluster specification (Queues, Parallel
Environments, RAM/Cores per node in queue, link to the SSH file, AEDT installation paths, etc)
3. copy [launcher_script.desktop](AEDT_Launcher/templates/launcher_script.desktop) to the same direction as 
[run_gui.py](AEDT_Launcher/run_gui.py) and modify the file. Set path to Python3 interpreter and absolute path to 
[run_gui.py](AEDT_Launcher/run_gui.py)
4. Install all required modules in your Python3 interpreter by running:
    ~~~
    python3 -m pip install -r requirements.txt
    ~~~
    where you need to specify relative or absolute path to [requirements.txt](AEDT_Launcher/requirements.txt)
5. you may need to set up your environment the way that each user has alias
    ~~~
    alias aedt '"/ekm/software/anaconda3/bin/python3" "/ott/apps/software/AEDT_Launcher/run_gui.py"'
    ~~~
6. you may need to automatically copy or create shortcut to 
[launcher_script.desktop](AEDT_Launcher/templates/launcher_script.desktop) for each user