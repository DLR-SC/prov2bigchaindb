import logging
import unittest
from prov2bigchaindb.tests.core import setup_test_files
from prov2bigchaindb.core import utils, clients
from bigchaindb_driver import BigchainDB

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class DocumentConceptTest(unittest.TestCase):
    """Test BigchainDB Base Client"""

    def setUp(self):
        self.bdb_connection = BigchainDB('http://127.0.0.1:9984')
        self.test_prov_files = setup_test_files()
        self.account_id = 'Document_Concept_Client_Test'

    def tearDown(self):
        del self.account_id
        db = utils.LocalStore()
        db.clean_tables()
        del db
        del self.bdb_connection
        [self.test_prov_files[k].close() for k in self.test_prov_files.keys()]

    # @unittest.skip("testing skipping")
    def test_simple_prov_doc(self):
        prov_document = utils.form_string(content=self.test_prov_files["simple"])
        client = clients.DocumentConceptClient(account_id=self.account_id)
        tx_id = client.save_document(prov_document)
        utils.wait_until_valid(tx_id, self.bdb_connection)
        doc = client.get_document(tx_id)
        self.assertEqual(len(prov_document.get_records()), len(doc.get_records()))
        self.assertEqual(prov_document, doc)

    # @unittest.skip("testing skipping")
    def test_simple2_prov_doc(self):
        prov_document = utils.form_string(content=self.test_prov_files["simple2"])
        client = clients.DocumentConceptClient(account_id=self.account_id)
        tx_id = client.save_document(prov_document)
        utils.wait_until_valid(tx_id, self.bdb_connection)
        doc = client.get_document(tx_id)
        self.assertEqual(len(prov_document.get_records()), len(doc.get_records()))
        self.assertEqual(prov_document, doc)

    # @unittest.skip("testing skipping")
    def test_thesis_prov_doc(self):
        prov_document = utils.form_string(content=self.test_prov_files["thesis"])
        client = clients.DocumentConceptClient(account_id=self.account_id)
        tx_id = client.save_document(prov_document)
        utils.wait_until_valid(tx_id, self.bdb_connection)
        doc = client.get_document(tx_id)
        self.assertEqual(len(prov_document.get_records()), len(doc.get_records()))
        self.assertEqual(prov_document, doc)

    # @unittest.skip("testing skipping")
    def test_quantified_prov_doc(self):
        prov_document = utils.form_string(content=self.test_prov_files["quantified"])
        client = clients.DocumentConceptClient(account_id=self.account_id)
        tx_id = client.save_document(prov_document)
        utils.wait_until_valid(tx_id, self.bdb_connection)
        doc = client.get_document(tx_id)
        self.assertEqual(len(prov_document.get_records()), len(doc.get_records()))
        self.assertEqual(prov_document, doc)