import unittest
from unittest import mock

from prov.graph import prov_to_graph
from prov2bigchaindb.core import utils, clients
from prov2bigchaindb.tests.core import setup_test_files
class BaseClientTest(unittest.TestCase):
    """Test BigchainDB Base Client"""

    def setUp(self):
        self.account_id = 'Base_Client_Test'
        self.public_key = 'public'
        self.private_key = 'private'
        self.host = '127.0.0.1'
        self.port = 9984

    def tearDown(self):
        pass

    @mock.patch('prov2bigchaindb.core.utils.LocalAccountStore', autospec=True)
    @mock.patch('bigchaindb_driver.BigchainDB', autospec=True)
    def test_positive_init_BaseClient(self, mock_bdb, mock_store):
        baseclient = clients.BaseClient(self.host, self.port)
        self.assertIsInstance(baseclient, clients.BaseClient)
        #self.assertIsInstance(baseclient.accountstore, utils.LocalAccountStore)
        self.assertIsInstance(baseclient.node, str)
        self.assertEqual(baseclient.node, 'http://127.0.0.1:9984')
        #TODO Check Instance of account_db

class DocumentConceptClientTest(unittest.TestCase):
    """Test BigchainDB Base Client"""

    def setUp(self):
        self.account_id = 'Base_Client_Test'
        self.public_key = 'public'
        self.private_key = 'private'
        self.host = '127.0.0.1'
        self.port = 9984
        self.test_prov_files = setup_test_files()
        self.prov_document = utils.form_string(content=self.test_prov_files["simple"])

    @mock.patch('prov2bigchaindb.core.utils.LocalAccountStore', autospec=True)
    @mock.patch('bigchaindb_driver.BigchainDB', autospec=True)
    @mock.patch('prov2bigchaindb.core.accounts.DocumentConceptAccount', autospec=True)
    def test_positive_init_DocumentModelClient(self, mock_account, mock_dbd, mock_store):
        doc_client = clients.DocumentConceptClient(self.account_id, self.host, self.port)
        self.assertIsInstance(doc_client, clients.DocumentConceptClient)
        #self.assertIsInstance(baseclient.accountstore, utils.LocalAccountStore)
        #self.assertIsInstance(baseclient.account, accounts.DocumentModelAccount)
        self.assertIsInstance(doc_client.node, str)
        self.assertEqual(doc_client.node, 'http://127.0.0.1:9984')
        # TODO Check Instance of account_db
        # TODO Check Instance of account

    def tearDown(self):
        [self.test_prov_files[k].close() for k in self.test_prov_files.keys()]

    @mock.patch('prov2bigchaindb.core.utils.LocalAccountStore', autospec=True)
    @mock.patch('bigchaindb_driver.BigchainDB', autospec=True)
    @mock.patch('prov2bigchaindb.core.accounts.DocumentConceptAccount', autospec=True)
    def test_get_document(self, mock_account, mock_dbd, mock_store):
        mock_account.query_Asset.return_value = {'asset':{'data':{'prov':self.prov_document.serialize(format='json')}}}
        doc_client = clients.DocumentConceptClient(self.account_id, self.host, self.port)
        doc_client.account = mock_account
        doc_client.connection = mock_dbd
        # Test
        document = doc_client.get_document('1')
        doc_client.account.query_Asset.assert_called_with('1', mock_dbd)
        self.assertEqual(document, self.prov_document)

    @mock.patch('prov2bigchaindb.core.utils.LocalAccountStore', autospec=True)
    @mock.patch('bigchaindb_driver.BigchainDB', autospec=True)
    @mock.patch('prov2bigchaindb.core.accounts.DocumentConceptAccount', autospec=True)
    def test_save_document(self, mock_account, mock_dbd, mock_store):
        mock_account.save_Asset.return_value = '1'
        doc_client = clients.DocumentConceptClient(self.account_id, self.host, self.port)
        doc_client.account = mock_account
        doc_client.connection = mock_dbd

        a = doc_client.save(self.prov_document)
        doc_client.account.save_Asset.assert_called_with({'data':{'prov':self.prov_document.serialize(format='json')}}, mock_dbd)
        self.assertIsInstance(a, str)
        self.assertEqual(a,'1')

