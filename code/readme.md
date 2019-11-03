# Code

This folder includes all used Python scripts and other code snippets. Below you find a short description of what the single file contain:

- `first_run.py`: Piecing together a first model run from start to finish
- `glen_a.py`: The script contains several routines which all perform a cross correlation between modeled and measured glacier length based on a combination of the ice creep parameter `glen_a`, the precipitation scaling factor `prcp_scaling_factor` and the "equilibrium" year `t_star`.
- `idaweb.py`: This file contains some routines to work with station data
  provided by the IDAWEB service (https://gate.meteoswiss.ch/idaweb/more.do)
- `mb_calibration.py`: Run the mass balance calibration, following the OGGM documentation (https://oggm.readthedocs.io/en/latest/run_examples/run_mb_calibration.html) and using the HISTALP climate data set.
- `mb_calibration_grindel.py`: Run the mass balance calibration for the Upper Grindelwald Glacier with different precipitation scaling factors.
- `mb_calibration_prepo.py`: Includes the needed preprocessing for the custom mass balance calibration process.
- `mycolors.py`: List of selected colors, which helps to have a consistent color scheme throughout a project.
- `process_histalp.py`: Combine the 'raw' HistAlp temperature and precipitation files into one data set and store it to file.
- `rgi-finder`: Shell script that searches information (coordinates, name) about glaciers, specified by RGI ID. 
- `t_star_tuning.py`: This script runs the flowline model for different values of `t_star` (between 1817
  and 1997) and stores the results.
- `utils.py`: Some utility routines that didn't fit anywhere else.