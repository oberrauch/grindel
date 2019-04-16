#!/usr/bin/env python

import numpy as np
import pandas as pd
import xarray as xr


def create_oggm_histalp_file(t_file, p_file, o_file,
                             ys=1801, ye=2014):

    # Function to rewrite the ZAMG HISTALP netCDF Data to a file which is
    # readable by oggm.core.climate.process_custom_climate_data
    #
    # ZAMG Datafiles from:
    # http://www.zamg.ac.at/histalp/dataset/grid/five_min.php
    # Two necessary files:
    # - Temperature Grid
    #               HISTALP_temperature_1780-2014.nc
    # - Total Precipitation Grid [mm]
    #               HISTALP_precipitation_all_abs_1801-2014.nc
    #
    # files and path must be provided as input
    # adaption could be made to download the data automatically
    #
    #
    # INPUT
    # t_file = path+filename of temperature grid.
    #          e.g. 'data/HISTALP_temperature_1780-2014.nc'
    # p_file = path+filename of precipitation grid.
    #          e.g. 'data/HISTALP_precipitation_all_abs_1801-2014.nc'
    # o_file = path+filename of output netcdf.
    #          e.g. 'data/histalp_merged.nc'
    # ys = Start year of requested time span. Default = 1801
    # ye = End year of requested time span (inclunding 01. Dec). Default = 2003

    # Define a reference date which will be used from here
    reference_date = pd.Timestamp('1801-01-01 00:00:00')

    # open HISTALP data files
    tdata = xr.open_dataset(t_file, decode_times=False)
    pdata = xr.open_dataset(p_file, decode_times=False)

    # loop over files to extract date information
    for data in [tdata, pdata]:
        # process HISTALP monthly data
        units = data.time.units
        # check if really monthly
        if units.split()[0] != 'months':
            raise Exception
        # check if there is data for every month
        if (np.diff(data.time.values) != 1).any():
            raise Exception

        # Only use YEAR and MONTH, not DAY
        # -> do not store monthly data at the middle of the month
        start = units.split()[2][0:7]
        periods = data.sizes['time']
        month = pd.date_range(start=start, periods=periods, freq='MS')
        days = (month - reference_date).days
        data.time.values = days.astype(float)
        data.time.attrs['units'] = 'days since %s' % reference_date

    # check if there is lat/lon matches
    if (tdata.lon.values-pdata.lon.values != 0).any():
        raise Exception
    if (tdata.lat.values-pdata.lat.values != 0).any():
        raise Exception

    # create output array with merge
    out = xr.merge([tdata, pdata]).astype(float)

    # some Attributes
    out.attrs['file_info'] = 'Merged HISTALP precipitation and temperature ' +\
        'dataset'
    out.attrs['data_author'] = 'Central Institute for Meteorology and ' +\
        'Geodynamics, Vienna, Austria (ZAMG)'
    out.attrs['references'] = 'http://www.zamg.ac.at/histalp'

    # rename variables according to OGGM usage
    out.rename({'HSURF': 'hgt',
                'T_2M': 'temp',
                'TOT_PREC': 'prcp'},
               inplace=True)

    out.temp.attrs['units'] = 'degC'
    out.prcp.attrs['units'] = 'mm'
    out.hgt.attrs['units'] = 'm'

    out = out.drop('ZONES')

    # select requested time period
    oindex = (pd.date_range(start=str(ys), end='%d-12-01' % ye, freq='MS') -
              reference_date).days
    out = out.loc[{'time': oindex}]

    # write to output path
    out.to_netcdf(o_file)


if __name__ == '__main__':

    # histalpfiles
    tfile = '../raw_data/HISTALP_temperature_1780-2014.nc'
    pfile = '../raw_data/HISTALP_precipitation_all_abs_1801-2014.nc'

    # outfile
    ofile = '../raw_data/histalp_merged_full.nc'

    # run function defined above
    create_oggm_histalp_file(tfile, pfile, ofile)
    pass
