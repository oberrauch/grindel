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
from oggm import cfg, utils
from oggm.utils import get_demo_file, get_rgi_glacier_entities
from oggm.core import gis, climate, centerlines, massbalance, flowline, inversion

from mb_calibration_grindel import mb_calib


def glen_a(factors, prcp_fac=None, ref_df=None, path=None,
           t_star=None, bias=0):
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
    if (t_star is not None) and (bias is not None):
        climate.local_t_star(gdir, tstar=t_star, bias=bias)
    else:
        climate.local_t_star(gdir, ref_df=ref_df)
    climate.mu_star_calibration(gdir)

    ## Mass balance
    # instance mass balance model using the historic climate file
    mb_model = massbalance.PastMassBalance(gdir)

    # store default values for Glen's A parameter
    inv_glen_a = cfg.PARAMS['inversion_glen_a']
    glen_a = cfg.PARAMS['glen_a']

    # create DataFrame
    df = pd.DataFrame(index=factors,
                      columns=['corr', 'rmsd', 'rmsd_bc', 'amp_diff'])

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
        fn = '/Users/oberrauch/work/grindelwald/data/length_ref_abs.csv'
        length_ref = pd.read_csv(fn, index_col=0)

        # combine both records
        length_df = pd.concat([length_ref, length_mod], axis=1)

        # get control data
        control = length_df.loc[1894:]
        # compute correlation coefficient
        corr = control.corr().iloc[0, 1]
        # compute rmsd anomaly
        rmsd = utils.rmsd(control.length_ref, control.model)
        rmsd_bc = utils.rmsd_bc(control.length_ref, control.model)

        # compute amplitude
        amp = control.max() - control.min()
        amp_diff = amp.diff().iloc[-1]

        # add to Dataframe
        df.loc[f] = [corr, rmsd, rmsd_bc, amp_diff]

    if path:
        # store to file
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
        ref_df = pd.read_csv(fn, index_col=0)
        # compute length correlation for different A parameters
        fp = '../data/length_corr_no_mb_calib/length_corr_prcp_fac_{:.2f}.csv'.format(prcp_fac)
        glen_a(factors, prcp_fac=prcp_fac, path=fp, ref_df=ref_df)


def cross_correlation_tstar_prcpfac_glena_files():
    # specify range of t* to test
    step = 5
    y0 = 1935
    y1 = 1960
    t_stars = np.arange(y0, y1+1, step)

    # iterate over all t*
    for t_star in t_stars:

        # iterate over different precipitation factors
        prcp_factors = np.linspace(1, 1.75, 4)
        for prcp_fac in prcp_factors:
            # define factors scaling the creep parameters
            factors = np.array([0.1, 0.5, 1, 2, 10])
            # read reference t* list
            # compute length correlation for different A parameters
            fp = ('../data/length_corr_t_star/length_corr_t_star_{:d}'
                  '_prcp_fac_{:.2f}.csv'.format(t_star, prcp_fac))
            glen_a(factors, prcp_fac=prcp_fac, path=fp, t_star=t_star)


def cross_correlation_tstar_prcpfac_glena(t_stars,
                                          prcp_factors,
                                          glen_a_factors):
    # create xarray Dataset with coordinates
    ds = xr.Dataset()
    # add coordinates
    ds.coords['t_star'] = ('t_star', t_stars)
    # TODO: add coordinate attributes
    ds['t_star'].attrs['description'] = 'Local t*'
    ds.coords['prcp_fac'] = ('prcp_fac', prcp_factors)
    ds.coords['glen_a_fac'] = ('glen_a_fac', glen_a_factors)

    # get shape of Dataset
    shape = [dim for dim in ds.dims.values()]
    # create dummy matrix, filled with NaN
    dummy = np.zeros(shape) * np.NaN

    # add variables and respective attributes
    ds['corr'] = (['glen_a_fac', 'prcp_fac', 't_star'], dummy.copy())
    ds['rmsd'] = (['glen_a_fac', 'prcp_fac', 't_star'], dummy.copy())
    ds['rmsd_bc'] = (['glen_a_fac', 'prcp_fac', 't_star'], dummy.copy())
    ds['amp_diff'] = (['glen_a_fac', 'prcp_fac', 't_star'], dummy.copy())

    # iterate over all t*
    for t_star in t_stars:
        # iterate over different precipitation factors
        for prcp_fac in prcp_factors:
            # define factors scaling the creep parameters

            # read reference t* list
            # compute length correlation for different A parameters
            df = glen_a(glen_a_factors, prcp_fac=prcp_fac, t_star=t_star)
            for glen_a_fac, row in df.iterrows():
                for column, value in row.iteritems():
                    ds[column].loc[dict(t_star=t_star,
                                        prcp_fac=prcp_fac,
                                        glen_a_fac=glen_a_fac)] = value

    return ds


if __name__ == '__main__':
    import time

    # specify range of t*
    step = 5
    y0 = 1935
    y1 = 1960
    t_stars = np.arange(y0, y1 + 1, step)
    # specify range of precipation scaling factor
    prcp_factors = np.linspace(1, 1.75, 4)
    # specify range of glen A scaling factor
    glen_a_factors = np.array([0.1, 0.5, 1, 2, 10])

    start = time.time()

    ds = cross_correlation_tstar_prcpfac_glena(t_stars,
                                               prcp_factors,
                                               glen_a_factors)

    print('Elapsed time:', time.time() - start, '[s]')

    path = '/Users/oberrauch/work/grindelwald/data/glen_a.nc'
    ds.to_netcdf(path)
