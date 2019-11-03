""" Piecing together a first model run from start to finish. """

# standard libraries
import numpy as np
import pandas as pd
# oggm modules
from oggm import utils, cfg, tasks, workflow, graphics
from oggm.core import flowline, massbalance, inversion, climate
from oggm.workflow import execute_entity_task
# system libraries
import os
# plotting libraries
import matplotlib
import matplotlib.pyplot as plt


def init_single_glacier(rgi_id, wdir=None, paths=None, params=None):
    """
    Performs the following necessary initialization steps for a single glacier:
        - loading the default path & parameter set
        - set/change config paths (given as arguments)
        - set/change config params (given as arguments)
        - downloading the corresponding RGI entry ()
        - creating/setting a local working directory
        - run the essential init_glacier_region() task
    Working directory is create if necessary, whereby it's named 'working_dir' if not
    specified as parameter.
    Returns the (path to the) glacier directory (gdir), if initialization was successful

    :param rgi_id: (str) RGI ID for glacier of interest
    :param wdir: (str, optional) name, and/or relative path to working directory
    :param paths: (dict, optional) path to be changed/set in config, following the
        style of cfg.PATHS dict: key=path_name, value=path
    :param params: (dict, optional) params to be changed/set in config, following the
        style of cfg.PARAMS dict: key=param_name, value=value
    :return: (str) path to the glacier directory
    """

    # load the OGGM parameter file
    cfg.initialize()

    # change/set paths in parameter file
    if paths is not None:
        for p, v in paths.items():
            cfg.PATHS[p] = v

    # change/set parameters in parameter file
    if params is not None:
        for p, v in params.items():
            cfg.PARAMS[p] = v

    # download RGI entry
    df_rgi = utils.get_rgi_glacier_entities([rgi_id])

    # define name of working directory if no given
    if wdir is None:
        wdir = os.path.join(os.getcwd(), 'working_dir')
    # create local working directory (where OGGM will write its output)
    utils.mkdir(wdir)
    # set path in config
    cfg.PATHS['working_dir'] = wdir
    # some user output
    print('Working directory: ', wdir)

    # Go - initialize working directories
    gdir = workflow.init_glacier_regions(df_rgi, reset=True)[0]

    return gdir


def prepo(gdir):
    """
    Runs all necessary preprocessing tasks for the given glacier directory, which are:
        - computing the glacier mask
        - computing the centerlines
        - initialize the flowlines
        - compute the downstream flowlines
        - compute the downstream bedshape
        - compute the catchement area of each tributary
        - compute the intersections between the catchments
        - compute the geometrical catchment widths (for each point of the flowline)
        - correct for NaNs and inconsistencies in the catchment widths

    :param gdir: path to glacier directory
    """
    # specify preprocessing tasks
    task_list = [
        tasks.glacier_masks,
        tasks.compute_centerlines,
        tasks.initialize_flowlines,
        tasks.compute_downstream_line,
        tasks.compute_downstream_bedshape,
        tasks.catchment_area,
        tasks.catchment_intersections,
        tasks.catchment_width_geom,
        tasks.catchment_width_correction
    ]
    # run all tasks
    for task in task_list:
        workflow.execute_entity_task(task, [gdir])
    pass


def cru_climate_tasks(gdir):
    """
    Execute the needed climate task when working with CRU data, which are
        - process and write the CRU climate data for this glacier
        - apply t* interpolation on this glacier
        - compute the apparent mass balance for the calculated mu*
    :param gdir: (str) path to glacier directory
    :return:
    """
    tasks.process_cru_data(gdir)
    tasks.distribute_t_stars([gdir])
    tasks.apparent_mb(gdir)
    pass


def histalp_climate_tasks(gdir, path_ref_tstar, path_histalp=None):
    """
    Execute the needed climate task when working with HISTALP (or any
    other custom climate) data, which are:
        - read the custom reference t* calibration list
        - set path to custom climate file
        - process and write the custom climate data for this glacier
        - apply t* interpolation on this glacier
        - compute the apparent mass balance for the calculated mu*
    Path to custom climate file must be given if not already set in cfg.PATHS.
    Mass balance calibration with custom climate file must be performed beforehand.

    :param gdir: (str) path to glacier directory
    :param path_ref_tstar: (str) path to custom reference t* calibration list
    :param path_histalp: (str, optional) path to custom climate file
    """
    # set the path to custom climate file if given as parameter
    if path_histalp is not None:
        cfg.PATHS['climate_file'] = path_histalp
    # read the reference t* calibration list
    ref_tstar = pd.read_csv(path_ref_tstar)
    # execute climate tasks
    tasks.process_custom_climate_data(gdir)
    tasks.distribute_t_stars([gdir], ref_df=ref_tstar)
    tasks.apparent_mb(gdir)
    pass


def thick_inversion(gdir, glen_a=None, fs=0.):
    """
    Executes the needed inversion tasks for this glacier, which are:
        - preparing the needed data
        - compute the ice thicknes inversion for this glacier
        - correct the last few (potentially noisy) grid points
            whilst conserving the total estimated volume
    Ice creep parameter and sliding factor can be passed as argument,
    otherwise the OGGM default values are used.
    :param gdir: path to glacier directory
    :param glen_a: (float, optional) creep parameter, 2.4e-24
    :param fs: ()
    """
    if not glen_a:
        glen_a = cfg.PARAMS['glen_a']
    tasks.prepare_for_inversion(gdir)
    tasks.volume_inversion(gdir, glen_a=glen_a, fs=fs)
    tasks.filter_inversion_output(gdir)
    pass


def cru():
    """ Use the above defined function to set up the model for the Upper Grindelwald Glacier
    and run it with the CRU climate data from 1902 to 2016.
    The glacier lenght evolution will be saved in the `histalp_lenght.csv` file.
    """

    # specify the RGI ID for the Upper Grindelwald Glacier
    rgi_id = 'RGI60-11.01270'
    # specify path to working directory
    wdir = '/Users/oberrauch/work/grindelwald/working_directories/first_run_wd'

    # specify parameters and corresponding values
    params = {
        'rgi_version': 6,
        'use_multiple_flowlines': True,
        'border': 70,
        'continue_on_error': False,
        'use_intersects': False,
        'run_mb_calibration': False

    }

    # initialize
    gdir = init_single_glacier(rgi_id, wdir=wdir, params=params)
    # preprocessing
    prepo(gdir)

    # climate - cru
    cru_climate_tasks(gdir)
    # print result of climate task to console
    # t*: year at which Grindelwald was in equilibrium
    # mu*: temperature sensitivity
    print(pd.read_csv(gdir.get_filepath('local_mustar')))

    # inversion
    thick_inversion(gdir)

    # final preparation for the run
    execute_entity_task(tasks.init_present_time_glacier, [gdir])

    # define massbalance model
    mbmod = massbalance.PastMassBalance(gdir)

    # run model for years with climate information
    flowline.robust_model_run(gdir, output_filesuffix='_cru',
                              mb_model=mbmod, ys=1902, ye=2016)

    # compile output - yields xarray
    ds = utils.compile_run_output([gdir], filesuffix='_cru')
    # convert xarray length data set into pandas series
    length = ds.length.to_series()
    # set name to 'cru'
    length.name = 'cru'
    # drop RGI ID index
    year_index = length.index.droplevel(level=1).astype(int)
    # exchange index
    length.index = year_index
    # write to file
    path = os.path.join(wdir, 'cru_length.csv')
    length.to_csv(path)

    pass


def histalp():
    """ Use the above defined function to set up the model for the Upper Grindelwald Glacier
    and run it with the HISTALP climate data from 1802 to 2003.
    The glacier lenght evolution will be saved in the `histalp_lenght.csv` file.
    """

    # specify the RGI ID for the Upper Grindelwald Glacier
    rgi_id = 'RGI60-11.01270'
    # specify path to working directory
    wdir = '/Users/oberrauch/work/grindelwald/working_directories/first_run_wd'

    # specify parameters and corresponding values
    params = {
        'rgi_version': 6,
        'use_multiple_flowlines': True,
        'border': 70,
        'continue_on_error': False,
        'use_intersects': False,
        'run_mb_calibration': True
    }

    # initialize
    gdir = init_single_glacier(rgi_id, wdir=wdir, params=params)
    # preprocessing
    prepo(gdir)

    # climate - histalp
    path_ref_tstar = '/Users/oberrauch/work/grindelwald/working_directories/mb_calib_wd/ref_tstars.csv'
    path_histalp = '/Users/oberrauch/work/grindelwald/raw_data/histalp_merged_full.nc'
    histalp_climate_tasks(gdir, path_ref_tstar, path_histalp)
    # print result of climate task to console
    # t*: year at which Grindelwald was in equilibrium
    # mu*: temperature sensitivity
    print(pd.read_csv(gdir.get_filepath('local_mustar')))

    # inversion
    thick_inversion(gdir)

    # final preparation for the run
    execute_entity_task(tasks.init_present_time_glacier, [gdir])

    # define massbalance model
    mbmod = massbalance.PastMassBalance(gdir)

    # run model for years with climate information
    flowline.robust_model_run(gdir, output_filesuffix='_histalp',
                              mb_model=mbmod, ys=1802, ye=2014)

    # compile output - yields xarray
    ds = utils.compile_run_output([gdir], filesuffix='_histalp')
    # convert xarray length data set into pandas series
    length = ds.length.to_series()
    # set name to 'histalp'
    length.name = 'histalp'
    # drop RGI ID index
    year_index = length.index.droplevel(level=1).astype(int)
    # exchange index
    length.index = year_index
    # write to file
    path = os.path.join(wdir, 'histalp_length.csv')
    length.to_csv(path)
    pass


def run(use_histalp=True):
    """ Use the above defined function to set up the model for the Upper Grindelwald Glacier
    and run it with the HISTALP climate data from 1802 to 2003.
    The glacier lenght evolution will be saved in the `histalp_lenght.csv` file.
    """

    # specify the RGI ID for the Upper Grindelwald Glacier
    rgi_id = 'RGI60-11.01270'
    # specify path to working directory
    wdir = '/Users/oberrauch/work/grindelwald/working_directories/first_run_wd'

    # specify parameters and corresponding values
    params = {
        'rgi_version': 6,
        'use_multiple_flowlines': True,
        'border': 70,
        'continue_on_error': False,
        'use_intersects': False,
        'run_mb_calibration': use_histalp
    }

    # initialize
    gdir = init_single_glacier(rgi_id, wdir=wdir, params=params)
    # preprocessing
    prepo(gdir)

    # run climate tasks
    if use_histalp:
        # climate - use_histalp
        path_ref_tstar = '/Users/oberrauch/work/grindelwald/working_directories/mb_calib_wd/ref_tstars.csv'
        path_histalp = '/Users/oberrauch/work/grindelwald/raw_data/histalp_merged_full.nc'
        histalp_climate_tasks(gdir, path_ref_tstar, path_histalp)
        # print result of climate task to console
        # t*: year at which Grindelwald was in equilibrium
        # mu*: temperature sensitivity
        print(pd.read_csv(gdir.get_filepath('local_mustar')))
        # set file name/suffix
        suff = 'histalp'
    else:
        # climate - cru
        cru_climate_tasks(gdir)
        # print result of climate task to console
        # t*: year at which Grindelwald was in equilibrium
        # mu*: temperature sensitivity
        print(pd.read_csv(gdir.get_filepath('local_mustar')))
        # set file name/suffix
        suff = 'cru'

    # inversion
    thick_inversion(gdir)

    # final preparation for the run
    execute_entity_task(tasks.init_present_time_glacier, [gdir])

    # define massbalance model
    mbmod = massbalance.PastMassBalance(gdir)

    # run model for years with climate information
    flowline.robust_model_run(gdir, output_filesuffix=suff,
                              mb_model=mbmod, ys=1802, ye=2014)

    # compile output - yields xarray
    ds = utils.compile_run_output([gdir], filesuffix=suff)
    # convert xarray length data set into pandas series
    length = ds.length.to_series()
    # set name to 'use_histalp'
    length.name = suff
    # drop RGI ID index
    year_index = length.index.droplevel(level=1).astype(int)
    # exchange index
    length.index = year_index
    # write to file
    path = os.path.join(wdir, '{}_length.csv'.format(suff))
    length.to_csv(path)
    pass


def read_and_plot():
    """ Read glacier lenght files and create plot. """

    # read all length files
    path = '/Users/oberrauch/work/grindelwald/raw_data/grindelwald_lengths_all.csv'
    length_lec = pd.read_csv(path, index_col=0, names=['lec'], skiprows=1)
    path = '/Users/oberrauch/work/grindelwald/working_directories/first_run_wd/cru_length.csv'
    length_cru = pd.read_csv(path, index_col=0, names=['cru'], skiprows=1)
    path = '/Users/oberrauch/work/grindelwald/working_directories/first_run_wd/histalp_length.csv'
    length_histalp = pd.read_csv(path, index_col=0, names=['histalp'], skiprows=1)

    # create single DataFrame out of all length records
    length_data = pd.concat([length_lec, length_histalp, length_cru], axis=1)

    # compute the offset between (measured) relative changes
    # and (modeled) absolute length
    offset_lec2hist = length_data[['lec', 'histalp']].dropna().iloc[0].diff().values[-1]
    # add offset to leclerq lenght changes
    length_data.lec += offset_lec2hist

    # eventually align CRU length data to new (i.e.) offset Leclerq data
    # offset_lec2cru = length_data[['lec', 'cru']].dropna().iloc[0].diff().values[-1]
    # length_data.cru -= offset_hist2cru

    # visualize
    length_data.plot(marker='.')
    plt.show()
    pass


if __name__ == '__main__':
    # run the glacier with CRU climate data
    # cru()
    # run(use_histalp=False)

    # run the glacier with HISTALP climate data
    histalp()
    run(use_histalp=True)
    
    # read the lenght data files and create plot
    read_and_plot()
    pass
