## v3.1.12
* prepend HOSTNAME to DISPLAY environment variable, 
eg if `DISPLAY=:3`, it will be converted to `DISPLAY=ottvnc3.ansys.com:3`

## [v3.1.9 - v3.1.11](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/commit/de12314f794ee4362af4c8fed3a12a0a6e9a0b4b)
* allow admin to specify environment variables in `cluster_configuration.json`
* if user saved settings and saved queue does not exist, set value to default queue
* remove spaces from node list value, users tend to put space after comma
* add error message if VNC/DCV host is unknown and not set in `cluster_configuration.json`

## [v3.1.8](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/commit/467beb856a6416d57391511672ef657ca074a643)
* remove AEDT build from the list, if build is inaccessible

## [v3.1.6 - v3.1.7](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/commit/fcb3c3f612ef8ccbedf1c291a7da17bcd73bb095)
* Disable radio button with interactive submission on DCV

## [v3.1.5](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/commit/e9ca8d7d37f95513506c008fa5593c83195fec58)
* OverWatch changed API, adopt

## [v3.1.5](https://github.com/beliaev-maksim/linux_hpc_launcher_slurm/commit/01a997ff2ceab2d0b89a95435aede2b320a29893)
* Change registry file for Slurm scheduler registration
* Remove reservation procedure that was leftover after SGE