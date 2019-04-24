## Import
# import externals libs
import os
import shutil
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt

# import OGGM modules
import oggm
from oggm import cfg, graphics, utils
from oggm.utils import get_demo_file, get_rgi_glacier_entities
from oggm.tests.funcs import get_test_dir
from oggm.core import gis, climate, centerlines, massbalance, flowline, inversion

from utils import get_leclercq_length, rmsd_anomaly
from mb_calibration_grindel import mb_calib


def glen_a(factors, prcp_fac=None, ref_df=None, path=None):
    """ Run model with different values for the creep parameter A and compute
    correlation and rmsd to length reference. Returns findings as DataFrame,
    and stores to file if path is given.

    :param path:
    :return:
    """

    ## Initialize
    # load default parameter file
    cfg.initialize()
    # specify working directory
    wdir = '/Users/oberrauch/work/grindelwald/working_directories/working_example/'
    cfg.PATHS['working_dir'] = wdir

    # set border high enough for idealized experiment
    cfg.PARAMS['border'] = 250

    # using intersects
    cfg.PARAMS['use_intersects'] = True

    # set climate/massbalance hyper parameters for HistAlp dataset
    cfg.PARAMS['baseline_climate'] = 'HISTALP'
    if prcp_fac:
        cfg.PARAMS['prcp_scaling_factor'] = prcp_fac
    else:
        cfg.PARAMS['prcp_scaling_factor'] = 1.75
    cfg.PARAMS['temp_melt'] = -1.75

    ## Preprocessing
    # get RGI entity
    rgi_id = 'RGI60-11.01270'
    rgi_df = get_rgi_glacier_entities([rgi_id], version='6')
    rgi_entity = rgi_df.iloc[0]
    rgi_df.plot()

    # specify intersects
    cfg.set_intersects_db(utils.get_rgi_intersects_region_file('11'))

    # prepare glacier directory
    gdir = oggm.GlacierDirectory(rgi_entity, reset=True)

    # ### GIS
    gis.define_glacier_region(gdir, entity=rgi_entity)
    gis.glacier_masks(gdir)

    # ### Centerlines
    centerlines.compute_centerlines(gdir)
    centerlines.initialize_flowlines(gdir)
    centerlines.compute_downstream_line(gdir)
    centerlines.compute_downstream_bedshape(gdir)
    centerlines.catchment_area(gdir)
    centerlines.catchment_intersections(gdir)
    centerlines.catchment_width_geom(gdir)
    centerlines.catchment_width_correction(gdir)

    ## Climate and mass balance parameters
    # process the HistAlp climate file
    climate.process_histalp_data(gdir)
    climate.local_t_star(gdir, ref_df=ref_df)
    climate.mu_star_calibration(gdir)

    ## Mass balance
    # instance mass balance model using the historic climate file
    mb_model = massbalance.PastMassBalance(gdir)

    # store default values for Glen's A parameter
    inv_glen_a = cfg.PARAMS['inversion_glen_a']
    glen_a = cfg.PARAMS['glen_a']

    # create DataFrame
    # df = pd.DataFrame(index=factors, columns=['correlation', 'rmsd', 'amp_diff', 'xcorr', 'xcorr_shift'])
    df = pd.DataFrame(index=factors, columns=['correlation', 'rmsd', 'amp_diff'])

    for f in factors:
        # Change the creep parameter
        cfg.PARAMS['inversion_glen_a'] = inv_glen_a * f
        cfg.PARAMS['glen_a'] = glen_a * f

        ## Inversion
        # run ice thicknes inversion
        inversion.prepare_for_inversion(gdir)
        inversion.mass_conservation_inversion(gdir)
        inversion.filter_inversion_output(gdir)

        ## Dynamic model
        # finalize the preprocessing
        flowline.init_present_time_glacier(gdir)

        ## Model
        # read needed file
        ci = gdir.read_pickle('climate_info')
        fls = gdir.read_pickle('model_flowlines')

        # now we can use the flowline model
        model = flowline.FluxBasedModel(fls, mb_model=mb_model,
                                        y0=ci['baseline_hydro_yr_0'])

        # run model over entire HistAlp period
        run_ds, diag_ds = model.run_until_and_store(2014)

        # get modeled length changes as DataFrame
        length_mod = diag_ds.length_m.to_dataframe()[['hydro_year', 'length_m']]
        length_mod = length_mod.reindex(index=length_mod.hydro_year)
        length_mod.drop('hydro_year', axis=1, inplace=True)
        length_mod.columns = ['model']

        # get reference length (Leclercq)
        length_ref = get_leclercq_length('11.01270')

        # combine both records
        length_df = pd.concat([length_ref, length_mod], axis=1)

        # get control data
        control = length_df.loc[1894:]
        # compute correlation coefficient
        corr = control.corr().iloc[0, 1]
        # compute rmsd anomaly
        rmsd = rmsd_anomaly(control.ref_dl, control.model)

        # compute amplitude
        amp = control.max() - control.min()
        amp_diff = amp.diff().iloc[-1]

        # compute cross correlation
        # shift = np.arange(-15, 15, 1)
        # xcorr = list()
        # for s in shift:
        #     ref_dl = control.ref_dl.shift(s)
        #     mod = control.model
        #     df_ = pd.concat([ref_dl, mod], axis=1).dropna()
        #     xcorr.append(df_.corr().iloc[0, 1])
        #
        # xcorr = pd.Series(xcorr, index=shift)
        # xcorr_shift = xcorr.idxmax()
        # xcorr = xcorr.max()

        # df.loc[f] = [corr, rmsd, amp_diff, xcorr, xcorr_shift]
        df.loc[f] = [corr, rmsd, amp_diff]

    if path:
        df.to_csv(path)

    # reset the creep parameter to default values
    cfg.PARAMS['inversion_glen_a'] = inv_glen_a
    cfg.PARAMS['glen_a'] = glen_a

    return df


def cross_correlation_with_mb_calibration():
    """

    :return:
    """
    # iterate over different precipitation factors
    prcp_factors = np.linspace(1, 1.75, 16)
    for prcp_fac in prcp_factors:
        # check if mb calibration already produced correct t* file
        fn = '{:.2f}'.format((prcp_fac)).replace('.', '_')
        fn = '/Users/oberrauch/work/grindelwald/ref_tstars/ref_tstars_prcp_{}.csv'.format(fn)
        if os.path.isfile(fn):
            # read prepared t* reference list
            ref_df = pd.read_csv(fn, index_col=0)
        else:
            # run mass balance calibration
            mb_calib(prcp_fac)
            # read t* reference list
            ref_df = pd.read_csv('/Users/oberrauch/oggm-fork/oggm/grindel/mb_calib_wd/ref_tstars.csv')
        # define factors scaling the creep parameters
        factors = np.concatenate((np.linspace(0.1, 1, 9, endpoint=False),
                                  np.linspace(1, 20, 20)))
        # compute length correlation for different A parameters
        fp = 'length_corr/length_corr_prcp_fac_{:.2f}.csv'.format(prcp_fac)
        glen_a(factors, prcp_fac=prcp_fac, ref_df=ref_df, path=fp)


def cross_correlation_without_mb_calibration():
    """

    :return:
    """
    # iterate over different precipitation factors
    prcp_factors = np.linspace(1, 1.75, 16)
    for prcp_fac in prcp_factors:
        # define factors scaling the creep parameters
        factors = np.concatenate((np.linspace(0.1, 1, 9, endpoint=False),
                                  np.linspace(1, 20, 20)))
        # read reference t* list
        fn = get_demo_file('oggm_ref_tstars_rgi6_histalp.csv')
        ref_df = ref_df = pd.read_csv(fn, index_col=0)
        # compute length correlation for different A parameters
        fp = '../data/length_corr_no_mb_calib/length_corr_prcp_fac_{:.2f}.csv'.format(prcp_fac)
        glen_a(factors, prcp_fac=prcp_fac, path=fp, ref_df=ref_df)


if __name__ == '__main__':
    cross_correlation_without_mb_calibration()
