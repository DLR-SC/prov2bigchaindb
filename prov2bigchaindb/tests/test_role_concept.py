import logging
import unittest

from prov2bigchaindb.core import clients, local_stores
from prov2bigchaindb.core import utils
from prov2bigchaindb.tests.core import setup_test_files

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class RoleConceptTest(unittest.TestCase):
    """Test BigchainDB Role Client"""

    def setUp(self):
        self.test_prov_files = setup_test_files()

    def tearDown(self):
        db = local_stores.BaseStore()
        db.clean_tables()
        del db

    # @unittest.skip("testing skipping")
    def test_simple_prov_doc(self):
        prov_document = utils.to_prov_document(content=self.test_prov_files["simple"])
        client = clients.GraphConceptClient()
        tx_ids = client.save_document(prov_document)
        doc = client.get_document(tx_ids)
        self.assertEqual(len(prov_document.get_records()), len(doc.get_records()))
        self.assertEqual(prov_document, doc)

    # @unittest.skip("testing skipping")
    def test_simple2_prov_doc(self):
        prov_document = utils.to_prov_document(content=self.test_prov_files["simple2"])
        client = clients.RoleConceptClient()
        tx_ids = client.save_document(prov_document)
        doc = client.get_document(tx_ids)
        self.assertEqual(len(prov_document.get_records()), len(doc.get_records()))
        self.assertEqual(prov_document, doc)
        print(tx_ids)

    # @unittest.skip("testing skipping")
    def test_thesis_prov_doc(self):
        prov_document = utils.to_prov_document(content=self.test_prov_files["thesis"])
        client = clients.RoleConceptClient()
        tx_ids = client.save_document(prov_document)
        doc = client.get_document(tx_ids)
        self.assertEqual(len(prov_document.get_records()), len(doc.get_records()))
        self.assertEqual(prov_document, doc)

    # @unittest.skip("testing skipping")
    def test_quantified_prov_doc(self):
        prov_document = utils.to_prov_document(content=self.test_prov_files["quantified"])
        client = clients.RoleConceptClient()
        tx_ids = client.save_document(prov_document)
        doc = client.get_document(tx_ids)
        self.assertEqual(len(prov_document.get_records()), len(doc.get_records()))
        self.assertEqual(prov_document, doc)
