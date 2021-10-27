## Description
This project aims to create a user-friendly interface to submit interactive Ansys Electronics Desktop (AEDT) jobs 
in a Linux environment.  
An interactive job means that the job will be submitted to the compute node using the Slurm scheduling system and 
will send back the desktop as a VNC session. This allows you to run resource 
intensive projects on powerful machines and interact with the AEDT graphical user interface.


## Configuration
In order to run AEDT Launcher on your cluster you need to perform following steps:
1. Clone the repository into your installation/app directory.
2. Copy [cluster_configuration.json](templates/cluster_configuration.json) to the same directory as
[run_gui.py](run_gui.py) and modify the file according to your cluster specification (Queues, Parallel
Environments, RAM/Cores per node in queue, link to the SSH file, AEDT installation paths, etc.)
3. Copy [launcher_script.desktop](templates/launcher_script.desktop) to the same directory as
[run_gui.py](run_gui.py) and modify the file. Set the path to the Python3 interpreter and absolute path to
[run_gui.py](run_gui.py)
4. Install the runtime requirements in your Python3 interpreter by running:
    ~~~
    python3 -m pip install -r requirements.txt
    ~~~
    where you need to specify relative or absolute path to [requirements.txt](requirements.txt)
5. You may need to set up your environment to include alias:
    ~~~
    alias aedt '"/ekm/software/anaconda3/bin/python3" "/ott/apps/software/AEDT_Launcher/run_gui.py"'
    ~~~
6. You may need to automatically copy or create shortcut to
[launcher_script.desktop](templates/launcher_script.desktop) for each user


## Contributing
You are welcome to contribute to this project.

You will need to install wxFormBuilder to build/update user interface from [AEDT_Launcher.fbp](gui/AEDT_Launcher.fbp).
We use version [3.9.0](https://github.com/wxFormBuilder/wxFormBuilder/releases/tag/v3.9.0)


## License
This project is licensed under the MIT license.  See [LICENSE](LICENSE)
