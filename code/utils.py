# ----------------
#  Import section
# ----------------

# gis modules
import ogr
import osr
import numpy as np
import pandas as pd
import xarray as xr

# oggm modules
from oggm.utils import get_rgi_glacier_entities, get_demo_file


def rgi_finder(rids, rgi_version='60'):
    """ Returns RGI entries for given RGI IDs in 'short' form.

    :param rids: (list of strings) RGI ID in the form region.glacier (eg. 11.01270)
    :param rgi_version: (str) RGI version, 6.0 as default
    :return: DataFrame with RGI entries, RGI ID as index
    """

    # specify RGI ID of glaciers of interest
    rids = ['RGI{}-{}'.format(rgi_version, rid) for rid in rids]

    # get said RGI entries
    rgi_dir = get_rgi_glacier_entities(rids, version=rgi_version)
    # set RGIId as index
    rgi_dir.index = rgi_dir.RGIId
    # delete RGIId column
    rgi_dir.drop(columns='RGIId', inplace=True)

    return rgi_dir


def convert_to_wgs84(lon, lat, EPSG):
    """ Converts point on projected coordinate system
    (specified via EPSG code) into WGS84 lon/lat coordinates.

    :param lon: (float) longitude in projected corrdinate system
    :param lat: (float) latitude in projected corrdinate system
    :param EPSG: (int) epsg code of projected corrdinate system
    :return: lon, lat in WGS84 coordinates
    """
    # specify WGS84 EPGS code
    EPSG_WGS84 = 4326

    # create a geometry from coordinates
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(lon, lat)
    # create coordinate transformation
    in_ref = osr.SpatialReference()
    in_ref.ImportFromEPSG(EPSG)
    out_ref = osr.SpatialReference()
    out_ref.ImportFromEPSG(EPSG_WGS84)
    coord_trans = osr.CoordinateTransformation(in_ref, out_ref)
    # transform point
    point.Transform(coord_trans)

    # return transformed coordinates
    return point.GetX(), point.GetY()

def get_leclercq_length(rgi_id):
    """ This functions does in essence the same as the function OGGM routine
    `GlacierDirectory.et_ref_length_data()`, i.e. reading the length records
    from the Leclercq data set. This routine does only works if you'r using the
    RGI version 5...

    :param rgi_id: (string) RGI ID in format region.glacier, e.g. 11.01270
    :return:
    """
    # get reference length record info (Leclercq)
    leclercq_df = pd.read_csv(get_demo_file('rgi_leclercq_links_2012_RGIV5.csv'))
    glacier = leclercq_df[leclercq_df.RGI_ID.str.contains(rgi_id)]
    # exit routine if no length records found
    if glacier.empty:
        raise RuntimeError('No length data found for this glacier!')

    # get length index (LID)
    index = glacier.LID.values
    # open the length data file
    f = get_demo_file('Glacier_Lengths_Leclercq.nc')
    with xr.open_dataset(f) as dsg:
        # the database is not sorted by ID. Don't ask me...
        grp_id = np.argwhere(dsg['index'].values == index)[0][0] + 1
    with xr.open_dataset(f, group=str(grp_id)) as ds:
        # read length records
        length_df = ds.dL.to_dataframe()
        length_df.columns = ['ref']
        length_df.name = ds.glacier_name

    return length_df


