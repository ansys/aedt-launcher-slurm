## [v3.2.3](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.2.2...v3.2.3)
* Fixed issue when multiple builds were corrupted and that caused mutation of the dictionary
* Print to console command that starts AEDT in batch/monitor/submit mode

## [v3.2.2](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.2.1...v3.2.2)
* Fixed issue when user was deleting nodes number and it was replaced by 1


## [v3.2.1](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.2.0...v3.2.1)
* Apply `black` style to `run_gui.py`

## [v3.2.0](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.1.12...v3.2.0)
* Enable product improvement by default
* Remove unused function
* Added `--debug` flag for future expansions
* Print `scancel` to terminal on cancel
* Do not export `ALL` variable when submit job 

## [v3.1.12](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.1.11...v3.1.12)
* Prepend HOSTNAME to DISPLAY environment variable, 
eg if `DISPLAY=:3`, it will be converted to `DISPLAY=ottvnc3.ansys.com:3`

## [v3.1.9 - v3.1.11](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.1.8...v3.1.11)
* Allow admin to specify environment variables in `cluster_configuration.json`
* If user saved settings and saved queue does not exist, set value to default queue
* Remove spaces from node list value, users tend to put space after comma
* Add error message if VNC/DCV host is unknown and not set in `cluster_configuration.json`

## [v3.1.8](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.1.7...v3.1.8)
* remove AEDT build from the list, if build is inaccessible

## [v3.1.6 - v3.1.7](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.1.5...v3.1.7)
* Disable radio button with interactive submission on DCV

## [v3.1.5](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.1.4...v3.1.5)
* OverWatch changed API, adopt

## [v3.1.4](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.1.3...v3.1.4)
* Change registry file for Slurm scheduler registration
* Remove reservation procedure that was leftover after SGE