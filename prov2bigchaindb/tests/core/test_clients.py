import unittest
from . import setup_test_files

from bigchaindb_driver.crypto import generate_keypair
from prov.graph import prov_to_graph

from prov2bigchaindb.core import utils, clients

TEST_DB_FILE = 'test.db'

class BaseClientTest(unittest.TestCase):
    """Test BigchainDB Base Client"""

    def setUp(self):
        pass

    def tearDown(self):
        pass


class DocumentModelClientTest(unittest.TestCase):
    """Test BigchainDB Base Client"""

    def setUp(self):
        self.instance = clients.DocumentModelClient('document_model_test_user', host='127.0.0.1', port=9984)
        self.private_key, self.public_key = generate_keypair()
        # open test files
        self.test_prov_files = setup_test_files()

    def tearDown(self):
        [self.test_prov_files[k].close() for k in self.test_prov_files.keys()]
        del self.instance

    def test_save_document(self):
        prov_document = utils.form_string(content=self.test_prov_files["simple"])
        a = self.instance.save(prov_document)
        self.assertIsInstance(a, str)

    def test_get_document(self):
        prov_document = utils.form_string(content=self.test_prov_files["simple"])
        tx_id = self.instance.save(prov_document)
        document = self.instance.get_document(tx_id)
        self.assertEqual(document, prov_document)
