import unittest
import pandas as pd

import code.utils as utils


class TestGrindelUtils(unittest.TestCase):
    """ Testing the utility methods for the Grindelwald project."""

    def test_rgi_finder(self):
        raise NotImplementedError

    def test_convert_to_wgs84(self):
        raise NotImplementedError

    def test_leclerq_length(self):
        # test with Oberen Grindelwald Gletscher
        # specify rgi id
        rgi_id = '11.01270'
        length_grindel = pd.read_csv('length_grindel.csv', index_col=0)
        length_ref = utils.get_leclercq_length(rgi_id)
        pd.testing.assert_frame_equal(length_ref, length_grindel,
                                      check_dtype=False)

        # test with Marmolada, which has no length records
        rgi_id = '11.03887'
        try:
            utils.get_leclercq_length(rgi_id)
            self.assertRaises(RuntimeError)
        except RuntimeError as e:
            e.args[0] == 'No length data found for this glacier!'

    def test_rmsd_anomaly(self):
        raise NotImplementedError
