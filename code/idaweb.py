import numpy as np
import pandas as pd
import os

index_columns = {
    'en': {
        'name': 'Filename',
        'type': 'Filetype',
        'station': 'Station',
        'param': 'Parameter',
        'period': 'Period'
    },
    'de': {
        'name': 'Dateiname',
        'type': 'Dateityp',
        'station': 'Station',
        'param': 'Parameter',
        'period': 'Zeitinterval'
    }
}

legend_file = {
    'en': {
        'station': 'Stations',
        'param': 'Parameter'
    },
    'de': {
        'station': 'Stationen',
        'param': 'Parameter'
    }
}


def list_files(order_path):
    """ Lists/sorts all files in the order directory and
    returns file names as list of strings.

    :param order_path: (str) relative or absolute path to order directory
    :return: index file name (str), list of legend files, list of data files
    """
    # get list of all files
    all_file = os.listdir(order_path)
    # get index file
    index = [f for f in all_file if 'index' in f]
    # index file exists either one or none
    if index:
        index = index[0]
    # get legend files
    legend = [f for f in all_file if 'legend' in f]
    # get data files
    data = [f for f in all_file if 'data' in f]

    return index, legend, data


def read_index_file(path, file_type='Data', lang='en'):
    # specify fixed column widths
    colspecs = [(0, 40), (40, 50), (50, 87), (87, 147), (147, 200)]
    # read the file
    data = pd.read_fwf(path, colspecs=colspecs, skiprows=7, encoding='latin-1')
    # subset data for specific file type
    if file_type and file_type != 'all':
        data = data.loc[data[index_columns[lang]['type']] == file_type]

    return data


def read_legend_file(path, encoding='latin-1', lang='en'):
    """

    :param path:
    :param encoding:
    :param lang:
    :return:
    """
    # open file
    fh = open(path, encoding=encoding)

    # dump all lines of file in dict whith line number as key
    lines = dict()
    for l_no, line in enumerate(fh):
        lines[l_no] = line.strip()

    # close file handler
    fh.close()

    # convert dictionary into Series, allowing
    # to search keys (indeces) by values
    lines = pd.Series(lines)

    # get start and end of station sections
    # starts with the heading 'Station' followed
    # by some horizonal lines and
    # ends with the paramter section
    start_line = lines[lines == legend_file[lang]['station']].index[0] + 2
    end_line = lines[lines == legend_file[lang]['param']].index[0] - 2

    # specify fixed column widths
    colspecs = [(0, 10), (10, 47), (47, 64), (64, 115), (115, 140), (140, 157), (157, 200)]

    # read station list from file
    stn = pd.read_fwf(path, colspecs=colspecs, encoding=encoding, index_col=0,
                      skiprows=lambda l: (l < start_line) or (l > end_line))

    # get start and end of parameter sections
    # starts with the heading 'Parameter' followed
    # by some horizonal lines and ends with the file
    start_line = lines[lines == legend_file[lang]['param']].index[0] + 2
    end_line = lines.size - 2

    # specify fixed column widths
    colspecs = [(0, 10), (10, 47), (47, 200)]

    # read parameter list from file
    param = pd.read_fwf(path, colspecs=colspecs, encoding=encoding, index_col=0,
                        skiprows=lambda l: (l < start_line) or (l > end_line))
    # return stations and parameter
    return stn, param


def read_data_file(path, date_parser=None, drop_station=True):

    # read file *.txt: values seperated by semicolon ';', encoding = Latin 1
    data = pd.read_csv(path, sep=';', encoding='latin-1', index_col=1,
                       parse_dates=[1], date_parser=date_parser, na_values='-')

    # eliminate station token as columns
    if drop_station:
        # get station label
        station = data.stn.values[-1]
        # remove column containing station label
        data.drop(columns='stn', inplace=True)
        # add station to column names
        data.columns = ['{}_{}'.format(c, station) for c in data.columns]

    return data


def get_wgs_limits(c_lon, c_lat, width, height, out='str'):
    """ Computes vertices window of given length and width around given centerpoint
    in WGS 84 coordinates. Default return type can be used in the IDAWEB data form.

    :param c_lon: (float) center longitude in WGS84 format
    :param c_lat: (float) center latitude in WGS84 format
    :param width: (float) window length (longitudinal) in km
    :param height: (float) window width (latitudinal) in km
    :param out: (str, optional) output format keyword
    :return: list with longitudinal and latitudinal limits
    """
    # Earth's radius at the equatorial plane in meters
    r_earth = 6.371e6
    # radius at latitudinal plane
    r_lat = np.sin(np.deg2rad(90 - c_lat)) * r_earth
    # circumference at latitudinal plane
    circ_lat = 2 * r_lat * np.pi

    # compute width of one longitudinal degree at current latitudinal plane
    deg_lon2m = circ_lat / 360
    # compute width of one latitudinal degree
    deg_lat2m = (2 * r_earth * np.pi) / 360

    # convert width and height into degrees lon/lat
    d_lon = width * 1e3 / deg_lon2m
    d_lat = height * 1e3 / deg_lat2m

    # compute min/max coordinates
    lon_limits = np.array([-d_lon, d_lon]) / 2 + c_lon
    lat_limits = np.array([-d_lat, d_lat]) / 2 + c_lat
    # round to specified precision
    dec_precision = 3
    lon_limits = np.around(lon_limits, decimals=dec_precision)
    lat_limits = np.around(lat_limits, decimals=dec_precision)

    # IDAWEB usable output format
    if out == 'str':
        # convert into degrees and minutes
        lon_deg = np.trunc(lon_limits).astype(int)
        lon_min = np.round(lon_limits % 1 * 60).astype(int)
        lat_deg = np.trunc(lat_limits).astype(int)
        lat_min = np.round(lat_limits % 1 * 60).astype(int)
        # bring into IDAWEB usable format
        lon_limits = "{d[0]}°{m[0]}'..{d[1]}°{m[1]}'".format(d=lon_deg, m=lon_min)
        lat_limits = "{d[0]}°{m[0]}'..{d[1]}°{m[1]}'".format(d=lat_deg, m=lat_min)

    return [lon_limits, lat_limits]
