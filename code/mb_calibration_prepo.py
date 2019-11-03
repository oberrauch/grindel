""" Includes the needed preprocessing for the custom mass balance
calibration process.
"""

# Python imports
from os import path

# Locals
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

# remove glaciers that are not in the HISTALP domain
rids_to_delete = ['RGI60-11.03232', 'RGI60-11.03209', 'RGI60-11.03241']
for rids_tmp in rids_to_delete:
    rids.remove(rids_tmp)

# Make a new DataFrame with those (this takes a while)
rgidf = utils.get_rgi_glacier_entities(rids, version=rgi_version)

# We have to check which of them actually have enough mb data.
# Let OGGM do it: first create GlacierDirectories
gdirs = workflow.init_glacier_regions(rgidf)
# We need to know which period we have data for
execute_entity_task(tasks.process_cru_data, gdirs, print_log=True)
gdirs = utils.get_ref_mb_glaciers(gdirs)
# Keep only these
rgidf = rgidf.loc[rgidf.RGIId.isin([g.rgi_id for g in gdirs])]

# save reference glaciers for the alps to file
raw_data_path = '/Users/oberrauch/work/grindelwald/raw_data'
rgidf.to_file(path.join(raw_data_path, 'mb_ref_glaciers_alps.shp'))

pass
