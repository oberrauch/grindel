# Notebooks

This directory contains all Jupyter Notebooks. Following is a list including a short description of each notebook:

## HistAlp climate comparison

- `prepare_idaweb_precip_data.ipynb`: First "contact" with the IDAWEB data... So it contains a lot of trial and error. The end product is a preprocessed monthly precipitation data set.
- `get_idaweb_data.ipynb`: covers the whole process of gathering station data from the IdaWeb service from start to finish. This includes the regional selection, parameter and station selection, preprocessing, outlier correction, ...
- `climate_comparison.ipynb`: assessing the  usability of the HistAlp dataset and compare it to actual climate records from the region
- `weather_station_map.ipynb`: producing an interactive map with Mapbox showing the different weather stations around the Grindelwald Glacier

## Calibration and validation

- `t_star_tuning.ipynb`: using the equilibrium year $t^*$ as model tuning parameter
- `prcp_scaling_A_param_tuning.ipynb`: using the combination of precipitation scaling parameter and the creep parameter (Glen's A parameter) as model tuning parameter
- `multi_param_multi_object_calibration.ipynb`: using the combination of $t^*$, `prcp_scaling` and `A` as model tuning parameter
- `reproduce_bac.ipynb`: reproducing all plots and computation made for my bachelors thesis

## Auxiliary notebook and sandbox:

- `length_reference.ipynb`: comparing different length change records (Leclercq and glamos.ch), converting length change into absolute glacier length

- `single_multiple_flowline.ipynb`: looking into the difference between a single flowline and multiple flowline model
- `shape_factor.ipynb`: looking into the influence of the bed shape factor (which parametrises lateral drag, ...)

- `bed_shape.ipynb`: looking into the influence of the bed shape (U-shaped, trapezoidal, parabolic
- `working_example.ipynb:` one of the first notebooks, piecing together a working model run from start to finish, additional comparison between model with and without spinup