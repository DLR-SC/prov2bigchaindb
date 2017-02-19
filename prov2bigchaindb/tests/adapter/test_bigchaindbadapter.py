import copy
import os
from prov2bigchaindb.adapter import BigchainDBAdapter
from bigchaindb_driver.crypto import generate_keypair
from datetime import datetime
import unittest

class BigchainDBAdapterTest(unittest.TestCase):
    """Test Bigchain Database Adapter"""

    def setUp(self):
        self.instance = BigchainDBAdapter(host='127.0.0.1', port=9984)
        self.private_key, self.public_key = generate_keypair()

    def tearDown(self):
        del self.instance

    def test_save_element(self):
        bicycle = {
            'data': {
                'bicycle': {
                    'serial_number': 'abcd1234',
                    'manufacturer': 'bkfab',
                },
            },
        }
        a = self.instance.save(attributes=bicycle, metadata={'test_time_stamp': str(datetime.now())}, public_key=self.public_key, private_key=self.private_key)
        self.assertIsInstance(a,str)
