import unittest
from datetime import datetime

from bigchaindb_driver.crypto import generate_keypair
from prov.graph import prov_to_graph

from prov2bigchaindb.core import utils
from prov2bigchaindb.core.client import DocumentModelClient


class BaseClientTest(unittest.TestCase):
    """Test BigchainDB Base Client"""

    def setUp(self):
        pass

    def tearDown(self):
        pass


class DocumentModelClientTest(unittest.TestCase):
    """Test BigchainDB Base Client"""

    def setUp(self):
        self.instance = DocumentModelClient('document_model_test_user', host='127.0.0.1', port=9984)
        self.private_key, self.public_key = generate_keypair()
        # open test files
        self.test_prov_files = utils.setup_test_files()

    def tearDown(self):
        [self.test_prov_files[k].close() for k in self.test_prov_files.keys()]
        del self.instance

    def test_save_element(self):
        prov_document = utils.form_string(content=self.test_prov_files["simple"])
        #a = self.instance.save(attributes=prov_document.serialize(format='json'), metadata={'test_time_stamp': str(datetime.now())}, public_key=self.public_key, private_key=self.private_key)
        a = self.instance.save(prov_document)
        self.assertIsInstance(a, str)
