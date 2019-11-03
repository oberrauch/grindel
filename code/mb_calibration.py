""" Run the mass balance calibration, following the OGGM documentation
and using the HISTALP climate data set.

https://oggm.readthedocs.io/en/latest/run_examples/run_mb_calibration.html
"""

# Python imports
from os import path

# Libs
import numpy as np

# Locals
import oggm
from oggm import cfg, utils, tasks, workflow
from oggm.workflow import execute_entity_task

# Module logger
import logging
log = logging.getLogger(__name__)

# RGI Version
rgi_version = '61'
rgi_region = '11'

# Initialize OGGM and set up the run parameters
cfg.initialize()

# Local paths (where to write the OGGM run output)
wdir = '/Users/oberrauch/work/grindelwald/working_directories/mb_calib_wd'
utils.mkdir(wdir, reset=True)
cfg.PATHS['working_dir'] = wdir

# We are running the calibration ourselves
cfg.PARAMS['run_mb_calibration'] = True

# No need for intersects since this has an effect on the inversion only
cfg.PARAMS['use_intersects'] = False

# Use multiprocessing?
cfg.PARAMS['use_multiprocessing'] = True

# Set to True for operational runs
cfg.PARAMS['continue_on_error'] = False

# Pre-download other files which will be needed later
_ = utils.get_cru_file(var='tmp')
_ = utils.get_cru_file(var='pre')
rgi_dir = utils.get_rgi_region_file(version=rgi_version, region=rgi_region)

# Get the reference glacier ids (they are different for each RGI version)
df, _ = utils.get_wgms_files()
rids = df['RGI{}0_ID'.format(rgi_version[0])]

# subset for central europe (RGI region 11)
rids = [rid for rid in rids if '-{}.'.format(rgi_region) in rid]

# remove glaciers that caused problems in prior runs
rids_to_delete = ['RGI60-11.03232', 'RGI60-11.03209', 'RGI60-11.03241']
for rids_tmp in rids_to_delete:
    rids.remove(rids_tmp)

# Make a new DataFrame with those (this takes a while)
log.info('Reading the RGI shape files...')
rgidf = utils.get_rgi_glacier_entities(rids, version=rgi_version)


# We have to check which of them actually have enough mb data.
# Let OGGM do it: first create GlacierDirectories
gdirs = workflow.init_glacier_regions(rgidf)
# We need to know which period we have data for
log.info('Process the climate data...')
execute_entity_task(tasks.process_cru_data, gdirs, print_log=True)
gdirs = utils.get_ref_mb_glaciers(gdirs)
# Keep only these
rgidf = rgidf.loc[rgidf.RGIId.isin([g.rgi_id for g in gdirs])]

# Save
log.info('For RGIV{} we have {} reference glaciers.'.format(rgi_version,
                                                            len(rgidf)))
rgidf.to_file(path.join(wdir, 'mb_ref_glaciers.shp'))

# rgidf = gpd.read_file(...)

# Sort for more efficient parallel computing
rgidf = rgidf.sort_values('Area', ascending=False)

# Go - initialize working directories
gdirs = workflow.init_glacier_regions(rgidf)

# Prepro tasks
task_list = [
    tasks.glacier_masks,
    tasks.compute_centerlines,
    tasks.initialize_flowlines,
    tasks.catchment_area,
    tasks.catchment_intersections,
    tasks.catchment_width_geom,
    tasks.catchment_width_correction,
]
# execute all tasks
for task in task_list:
    execute_entity_task(task, gdirs)

# set path to HISTALP climate file
cfg.PATHS['climate_file'] = '/Users/oberrauch/work/grindelwald/raw_data/histalp_merged_full.nc'
# Climate tasks
execute_entity_task(tasks.process_custom_climate_data, gdirs)
tasks.compute_ref_t_stars(gdirs)
tasks.distribute_t_stars(gdirs)
execute_entity_task(tasks.apparent_mb, gdirs)
# Recompute after the first round - this is being picky but this is
# Because geometries may change after apparent_mb's filtering
tasks.compute_ref_t_stars(gdirs)
tasks.distribute_t_stars(gdirs)
execute_entity_task(tasks.apparent_mb, gdirs)

# log
log.info('Skipping the testing...')

# Log
log.info('Calibration is done!')
pass
