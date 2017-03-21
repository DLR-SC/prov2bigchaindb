import logging
import os
import unittest
from prov2bigchaindb.tests.core import setup_test_files
from prov2bigchaindb.core import utils, clients, local_stores
from bigchaindb_driver import BigchainDB

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DocumentConceptTest(unittest.TestCase):
    """Test BigchainDB Document Concept"""

    def setUp(self):
        self.host="0.0.0.0"
        self.port=9984
        if os.environ.get('BDB_HOST'):
            self.host = os.environ.get('BDB_HOST')
        if os.environ.get('BDB_PORT'):
            self.port = int(os.environ.get('BDB_PORT'))
        self.bdb_connection = BigchainDB('http://{}:{}'.format(self.host,self.port))
        self.test_prov_files = setup_test_files()
        self.account_id = 'Document_Concept_Client_Test'

    def tearDown(self):
        del self.account_id
        del self.host
        del self.port
        db = local_stores.SqliteStore()
        db.clean_tables()
        del db
        del self.bdb_connection
        del self.test_prov_files

    @unittest.skip("testing skipping")
    def test_simple_prov_doc(self):
        prov_document = utils.to_prov_document(content=self.test_prov_files["simple"])
        doc_client = clients.DocumentConceptClient(account_id=self.account_id, host=self.host, port=self.port)
        tx_id = doc_client.save_document(prov_document)
        utils.wait_until_valid(tx_id, self.bdb_connection)
        doc = doc_client.get_document(tx_id)
        self.assertEqual(len(prov_document.get_records()), len(doc.get_records()))
        self.assertEqual(prov_document, doc)

    #@unittest.skip("testing skipping")
    def test_simple2_prov_doc(self):
        prov_document = utils.to_prov_document(content=self.test_prov_files["simple2"])
        doc_client = clients.DocumentConceptClient(account_id=self.account_id, host=self.host, port=self.port)
        tx_id = doc_client.save_document(prov_document)
        utils.wait_until_valid(tx_id, self.bdb_connection)
        doc = doc_client.get_document(tx_id)
        self.assertEqual(len(prov_document.get_records()), len(doc.get_records()))
        self.assertEqual(prov_document, doc)

    @unittest.skip("testing skipping")
    def test_thesis_prov_doc(self):
        prov_document = utils.to_prov_document(content=self.test_prov_files["thesis"])
        doc_client = clients.DocumentConceptClient(account_id=self.account_id, host=self.host, port=self.port)
        tx_id = doc_client.save_document(prov_document)
        utils.wait_until_valid(tx_id, self.bdb_connection)
        doc = doc_client.get_document(tx_id)
        self.assertEqual(len(prov_document.get_records()), len(doc.get_records()))
        self.assertEqual(prov_document, doc)

    @unittest.skip("testing skipping")
    def test_quantified_prov_doc(self):
        prov_document = utils.to_prov_document(content=self.test_prov_files["quantified"])
        doc_client = clients.DocumentConceptClient(account_id=self.account_id, host=self.host, port=self.port)
        tx_id = doc_client.save_document(prov_document)
        utils.wait_until_valid(tx_id, self.bdb_connection)
        doc = doc_client.get_document(tx_id)
        self.assertEqual(len(prov_document.get_records()), len(doc.get_records()))
        self.assertEqual(prov_document, doc)
