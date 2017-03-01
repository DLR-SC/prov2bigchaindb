import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from prov2bigchaindb.core.utils import LocalStore
import unittest
from unittest import mock
from prov2bigchaindb.tests.core import setup_test_files
from prov2bigchaindb.core import utils, clients

class GraphConceptTest(unittest.TestCase):
    """Test BigchainDB Base Client"""

    def setUp(self):
        self.test_prov_files = setup_test_files()

    def tearDown(self):
        [self.test_prov_files[k].close() for k in self.test_prov_files.keys()]

    #@unittest.skip("testing skipping")
    def test_simple_prov_doc(self):
        prov_document = utils.form_string(content=self.test_prov_files["simple"])
        client = clients.GraphConceptClient()
        tx_ids = client.save_document(prov_document)
        doc = client.get_document(tx_ids)
        self.assertEqual(prov_document, doc)

        db = LocalStore()
        db.clean_tables()
        del db


        #prov_document = utils.form_string(content=self.test_prov_files["thesis"])
        #client = clients.GraphConceptClient()
        #tx_id = client.save_document(prov_document)
        #ret_doc = client.get_document(tx_id)
        #self.assertEqual(prov_document,ret_doc)

