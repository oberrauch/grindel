# ----------------
#  Import section
# ----------------

# gis modules
import ogr, osr

# oggm modules
from oggm.utils import get_rgi_glacier_entities


def rgi_finder(rids, rgi_version='60'):
    """Returns RGI entries for given RGI IDs in 'short' form.

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
