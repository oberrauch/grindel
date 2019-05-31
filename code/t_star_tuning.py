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
from oggm.utils import get_demo_file, get_rgi_glacier_entities, rmsd
from oggm.tests.funcs import get_test_dir
from oggm.core import gis, climate, centerlines, massbalance, flowline, inversion

# import my modules
import sys
from utils import rmsd_anomaly, get_leclercq_length

## Initilize
# load default parameter file
cfg.initialize()
# specify working directory
wdir = '/Users/oberrauch/work/grindelwald/working_directories/t_star_tuning_wd/'
cfg.PATHS['working_dir'] = wdir

# using intersects
cfg.PARAMS['use_intersects'] = True

# define big border
cfg.PARAMS['border'] = 250

# set climate/massbalance hyper parameters for HistAlp dataset
cfg.PARAMS['baseline_climate'] = 'HISTALP'
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

# GIS tasks
gis.define_glacier_region(gdir, entity=rgi_entity)
gis.glacier_masks(gdir)

# run center line preprocessing tasks
centerlines.compute_centerlines(gdir)
centerlines.initialize_flowlines(gdir)
centerlines.compute_downstream_line(gdir)
centerlines.compute_downstream_bedshape(gdir)
centerlines.catchment_area(gdir)
centerlines.catchment_intersections(gdir)
centerlines.catchment_width_geom(gdir)
centerlines.catchment_width_correction(gdir)

# process the HistAlp climate file
climate.process_histalp_data(gdir)
# read climate info file
ci = gdir.read_pickle('climate_info')
y0 = ci['baseline_hydro_yr_0']
y1 = ci['baseline_hydro_yr_1']

# specify range of t* to test
step = 5
mu_hp = int(cfg.PARAMS['mu_star_halfperiod'])
t_stars = np.arange(y0+mu_hp, y1-mu_hp, step)

# init empty container to store glacier length evolution
length = pd.DataFrame(columns=np.arange(y0, y1+1))
length.index.name = 't_star'

for t_star in t_stars:
    climate.local_t_star(gdir, tstar=t_star, bias=0)
    climate.mu_star_calibration(gdir)

    # instance mass balance model using the historic climate file
    mb_model = massbalance.PastMassBalance(gdir)

    # run ice thicknes inversion
    inversion.prepare_for_inversion(gdir)
    inversion.mass_conservation_inversion(gdir)
    inversion.filter_inversion_output(gdir)

    # finalize the preporcessing
    flowline.init_present_time_glacier(gdir)

    # read flowlines from file
    fls = gdir.read_pickle('model_flowlines')
    # now we can use the flowline model
    model = flowline.FluxBasedModel(fls, mb_model=mb_model, y0=y0)
    # run model over entire HistAlp period
    run_ds, diag_ds = model.run_until_and_store(y1)

    length.loc[t_star] = diag_ds.length_m.to_dataframe()['length_m']

# add reference length changes
length_ref = get_leclercq_length(rgi_id='11.01270')
length = length.append(length_ref.T)
length.index.name = 't_stars'

# store DataFrame to file
length.to_csv('/Users/oberrauch/work/grindelwald/data/length_t_star.csv')