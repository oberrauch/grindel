""" Run the mass balance calibration for the Upper Grindelwald Glacier
with different precipitation scaling factors.
"""

# Python imports
import json
import os

# Libs
import numpy as np

# Locals
from oggm import cfg, utils, tasks, workflow
from oggm.workflow import execute_entity_task


def mb_calib(prcp_fac):
    # RGI Version
    rgi_version = '61'

    # Initialize OGGM and set up the run parameters
    cfg.initialize(logging_level='WORKFLOW')

    # Local paths (where to write the OGGM run output)
    WORKING_DIR = os.path.join(os.getcwd(), 'mb_calib_wd')
    utils.mkdir(WORKING_DIR, reset=True)
    cfg.PATHS['working_dir'] = WORKING_DIR


    # The following code block alters certain parameters from
    # the default config file.

    # We are running the calibration ourselves
    cfg.PARAMS['run_mb_calibration'] = True

    # We are using which baseline data?
    cfg.PARAMS['baseline_climate'] = 'HISTALP'

    # No need for intersects since this has an effect on the inversion only
    cfg.PARAMS['use_intersects'] = False

    # Use multiprocessing?
    cfg.PARAMS['use_multiprocessing'] = False

    # Set to True for operational runs
    cfg.PARAMS['continue_on_error'] = False

    # Other params: see https://oggm.org/2018/08/10/histalp-parameters/
    # a different mass balance model?!
    cfg.PARAMS['baseline_y0'] = 1850
    cfg.PARAMS['prcp_scaling_factor'] = prcp_fac
    cfg.PARAMS['temp_melt'] = -1.75

    # The next step is to get all the reference glaciers,
    # i.e. glaciers with mass balance measurements.

    # Get the reference glacier ids (they are different for each RGI version)
    rgi_dir = utils.get_rgi_dir(version=rgi_version)
    df, _ = utils.get_wgms_files()
    rids = df['RGI{}0_ID'.format(rgi_version[0])]

    # We can't do Antarctica
    rids = [rid for rid in rids if not ('-19.' in rid)]

    # For HISTALP only RGI reg 11
    rids = [rid for rid in rids if '-11.' in rid]

    # Make a new dataframe with those (this takes a while)
    print('Reading the RGI shapefiles...')
    rgidf = utils.get_rgi_glacier_entities(rids, version=rgi_version)
    print('For RGIV{} we have {} candidate reference '
          'glaciers.'.format(rgi_version, len(rgidf)))

    # save those reference glaciers in a separate DataFrame
    rgidf_alps = rgidf.copy()

    # initialize the glacier regions
    gdirs = workflow.init_glacier_regions(rgidf_alps)

    # we need to know which period we have data for
    # some glaciers are not in Alps
    cfg.PARAMS['continue_on_error'] = True
    execute_entity_task(tasks.process_histalp_data, gdirs, print_log=False)
    cfg.PARAMS['continue_on_error'] = False

    gdirs = utils.get_ref_mb_glaciers(gdirs)

    # Keep only these
    rgidf = rgidf.loc[rgidf.RGIId.isin([g.rgi_id for g in gdirs])]

    # Save
    print('For RGIV{} and {} we have {} reference glaciers.'.format(rgi_version,
                                                                    'HISTALP',
                                                                    len(rgidf)))
    rgidf.to_file(os.path.join(WORKING_DIR, 'mb_ref_glaciers.shp'))

    # Sort for more efficient parallel computing
    rgidf = rgidf.sort_values('Area', ascending=False)

    # Go - initialize glacier directories
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
    for task in task_list:
        execute_entity_task(task, gdirs)

    # Climate tasks
    tasks.compute_ref_t_stars(gdirs)
    execute_entity_task(tasks.local_t_star, gdirs)
    execute_entity_task(tasks.mu_star_calibration, gdirs)

    # We store the associated params
    mb_calib = gdirs[0].read_pickle('climate_info')['mb_calib_params']
    with open(os.path.join(WORKING_DIR, 'mb_calib_params.json'), 'w') as fp:
        json.dump(mb_calib, fp)


if __name__ == '__main__':
    prcp_factors = np.linspace(1, 1.75, 16)
    for prcp_fac in prcp_factors:
        # run mass balance calibration
        mb_calib(prcp_fac)
        # add prcp scaling factor to file name
        src = os.path.join(cfg.PATHS['working_dir'], 'ref_tstars.csv')
        dir = '/Users/oberrauch/work/grindelwald/ref_tstars'
        fn = 'ref_tstars_prcp_{:.2f}'.format(prcp_fac).replace('.', '_') + '.csv'
        dst = os.path.join(dir, fn)
        os.rename(src, dst)

