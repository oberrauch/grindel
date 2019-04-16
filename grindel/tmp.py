## Import
# import externals libs
import pandas as pd

# import OGGM modules
import oggm
from oggm import cfg, graphics, utils
from oggm.utils import get_rgi_glacier_entities

from oggm.core import gis, climate, centerlines, massbalance, flowline, inversion


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
climate.local_t_star(gdir)
climate.mu_star_calibration(gdir)

## Mass balance
# instance mass balance model using the historic climate file
mb_model = massbalance.PastMassBalance(gdir)

## Inversion
# run ice thicknes inversion
inversion.prepare_for_inversion(gdir)
inversion.mass_conservation_inversion(gdir)
inversion.filter_inversion_output(gdir)

## Dynamic model
# finalize the preprocessing
flowline.init_present_time_glacier(gdir)

# plot flowlines
graphics.plot_centerlines(gdir, use_model_flowlines=True)
