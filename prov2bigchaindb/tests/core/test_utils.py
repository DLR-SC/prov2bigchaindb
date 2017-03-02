import logging
import unittest

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class UtilityTest(unittest.TestCase):
    def setUp(self):
        self.account_id = 'Utility_Test_Account'
        self.public_key = 'public'
        self.private_key = 'private'

    def tearDown(self):
        del self.account_id
        del self.public_key
        del self.private_key

    @unittest.skip("testing skipping")
    def test_form_string(self):
        raise NotImplementedError()

    @unittest.skip("testing skipping")
    def test_wait_until_valid(self):
        raise NotImplementedError()

    @unittest.skip("testing skipping")
    def test_is_valid_tx(self):
        raise NotImplementedError()

    @unittest.skip("testing skipping")
    def test_is_block_to_tx_valid(self):
        raise NotImplementedError()

    @unittest.skip("testing skipping")
    def test_get_prov_element_list(self):
        raise NotImplementedError()
