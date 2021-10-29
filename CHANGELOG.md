## [v3.2.1](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.2.0...v3.2.1)
* apply `black` style to `run_gui.py`

## [v3.2.0](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.1.12...v3.2.0)
* enable product improvement by default
* remove unused function
* added `--debug` flag for future expansions
* print `scancel` to terminal on cancel
* Do not export `ALL` variable when submit job 

## [v3.1.12](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.1.11...v3.1.12)
* prepend HOSTNAME to DISPLAY environment variable, 
eg if `DISPLAY=:3`, it will be converted to `DISPLAY=ottvnc3.ansys.com:3`

## [v3.1.9 - v3.1.11](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.1.8...v3.1.11)
* allow admin to specify environment variables in `cluster_configuration.json`
* if user saved settings and saved queue does not exist, set value to default queue
* remove spaces from node list value, users tend to put space after comma
* add error message if VNC/DCV host is unknown and not set in `cluster_configuration.json`

## [v3.1.8](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.1.7...v3.1.8)
* remove AEDT build from the list, if build is inaccessible

## [v3.1.6 - v3.1.7](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.1.5...v3.1.7)
* Disable radio button with interactive submission on DCV

## [v3.1.5](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.1.4...v3.1.5)
* OverWatch changed API, adopt

## [v3.1.4](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/compare/v3.1.3...v3.1.4)
* Change registry file for Slurm scheduler registration
* Remove reservation procedure that was leftover after SGE