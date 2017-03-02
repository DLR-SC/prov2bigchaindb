import logging
import unittest
from prov2bigchaindb.tests.core import setup_test_files
from prov2bigchaindb.core import utils, clients

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class GraphConceptTest(unittest.TestCase):
    """Test BigchainDB Base Client"""

    def setUp(self):
        self.test_prov_files = setup_test_files()

    def tearDown(self):
        db = utils.LocalStore()
        db.clean_tables()
        del db
        [self.test_prov_files[k].close() for k in self.test_prov_files.keys()]

    # @unittest.skip("testing skipping")
    def test_simple_prov_doc(self):
        prov_document = utils.form_string(content=self.test_prov_files["simple"])
        client = clients.GraphConceptClient()
        tx_ids = client.save_document(prov_document)
        doc = client.get_document(tx_ids)
        self.assertEqual(len(prov_document.get_records()), len(doc.get_records()))
        self.assertEqual(prov_document, doc)

    # @unittest.skip("testing skipping")
    def test_simple2_prov_doc(self):
        prov_document = utils.form_string(content=self.test_prov_files["simple2"])
        client = clients.GraphConceptClient()
        tx_ids = client.save_document(prov_document)
        doc = client.get_document(tx_ids)
        self.assertEqual(len(prov_document.get_records()), len(doc.get_records()))
        self.assertEqual(prov_document, doc)

    # @unittest.skip("testing skipping")
    def test_thesis_prov_doc(self):
        prov_document = utils.form_string(content=self.test_prov_files["thesis"])
        client = clients.GraphConceptClient()
        tx_ids = client.save_document(prov_document)
        doc = client.get_document(tx_ids)
        self.assertEqual(len(prov_document.get_records()), len(doc.get_records()))
        self.assertEqual(prov_document, doc)


    # @unittest.skip("testing skipping")
    def test_quantified_prov_doc(self):
        prov_document = utils.form_string(content=self.test_prov_files["quantified"])
        client = clients.GraphConceptClient()
        tx_ids = client.save_document(prov_document)
        doc = client.get_document(tx_ids)
        self.assertEqual(len(prov_document.get_records()), len(doc.get_records()))
        self.assertEqual(prov_document, doc)
