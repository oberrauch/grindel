# import
import numpy as np
import pandas as pd
import xarray as xr
from oggm.utils import get_demo_file


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


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    # specify rgi id
    rgi_id = '11.00897'
    length_ref = get_leclercq_length(rgi_id)
    plt.plot(length_ref)
    plt.show()


