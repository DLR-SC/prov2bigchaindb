import logging
import unittest
from time import sleep
from unittest import mock

from bigchaindb_driver import pool as bdpool

from prov2bigchaindb.core import utils, clients
from prov2bigchaindb.tests.core import setup_test_files

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class BaseClientTest(unittest.TestCase):
    """Test BigchainDB Base Client"""

    def setUp(self):
        self.account_id = 'Base_Client_Test'
        self.public_key = 'public'
        self.private_key = 'private'
        self.host = '127.0.0.1'
        self.port = 9984

    def tearDown(self):
        del self.account_id
        del self.public_key
        del self.private_key
        del self.host
        del self.port

    @mock.patch('prov2bigchaindb.core.clients.local_stores.SqliteStore')
    @mock.patch('prov2bigchaindb.core.clients.bd.BigchainDB')
    def test_positive_init(self, mock_bdb, mock_store):
        baseclient = clients.BaseClient(self.host, self.port)
        baseclient.connection = mock_bdb
        baseclient.accountstore = mock_store
        self.assertIsInstance(baseclient, clients.BaseClient)
        # self.assertIsInstance(baseclient.accountstore, utils.LocalAccountStore)
        self.assertIsInstance(baseclient.node, str)
        self.assertEqual(baseclient.node, 'http://127.0.0.1:9984')
        # TODO Check Instance of account_db

    @unittest.skip("testing skipping")
    def test_test_transaction(self):
        raise NotImplementedError()

    @mock.patch('prov2bigchaindb.core.clients.local_stores.SqliteStore')
    @mock.patch('prov2bigchaindb.core.clients.bd.BigchainDB')
    def test_save_document(self, mock_bdb, mock_store):
        baseclient = clients.BaseClient(self.host, self.port)
        baseclient.connection = mock_bdb
        baseclient.accountstore = mock_store
        with self.assertRaises(NotImplementedError):
            baseclient.save_document('foo')


class DocumentConceptClientTest(unittest.TestCase):
    """Test BigchainDB Base Client"""

    def setUp(self):
        self.account_id = 'Document_Client_Test'
        self.public_key = 'public'
        self.private_key = 'private'
        self.host = '127.0.0.1'
        self.port = 9984
        self.test_prov_files = setup_test_files()
        self.prov_document = utils.to_prov_document(content=self.test_prov_files["simple"])

    def tearDown(self):
        del self.account_id
        del self.public_key
        del self.private_key
        del self.host
        del self.port
        del self.test_prov_files
        del self.prov_document

    @mock.patch('prov2bigchaindb.core.clients.local_stores.SqliteStore')
    @mock.patch('prov2bigchaindb.core.clients.bd.BigchainDB')
    @mock.patch('prov2bigchaindb.core.clients.accounts.DocumentConceptAccount')
    def test_positive_init(self, mock_account, mock_dbd, mock_store):
        doc_client = clients.DocumentConceptClient(self.account_id, self.host, self.port)
        self.assertIsInstance(doc_client, clients.DocumentConceptClient)
        # self.assertIsInstance(baseclient.accountstore, utils.LocalAccountStore)
        # self.assertIsInstance(baseclient.account, accounts.DocumentModelAccount)
        self.assertIsInstance(doc_client.node, str)
        self.assertEqual(doc_client.node, 'http://127.0.0.1:9984')
        # TODO Check Instance of account_db
        # TODO Check Instance of account

    @mock.patch('prov2bigchaindb.core.clients.utils.is_valid_tx')
    @mock.patch('prov2bigchaindb.core.clients.utils.is_block_to_tx_valid')
    @mock.patch('prov2bigchaindb.core.clients.local_stores.SqliteStore')
    @mock.patch('prov2bigchaindb.core.clients.bd.BigchainDB')
    @mock.patch('prov2bigchaindb.core.clients.accounts.DocumentConceptAccount')
    def test_get_document(self, mock_account, mock_bdb, mock_store, mock_test_block, mock_test_tx):
        mock_bdb.transactions.retrieve.return_value = {'id': '1', 'asset': {
            'data': {'prov': self.prov_document.serialize(format='json')}}}
        mock_test_block.return_value = True
        mock_test_tx.return_value = True
        doc_client = clients.DocumentConceptClient(self.account_id, self.host, self.port)
        doc_client.account = mock_account
        doc_client.connection_pool = bdpool.Pool([mock_bdb])
        # Test
        document = doc_client.get_document('1')
        sleep(1)
        doc_client._get_bigchain_connection().transactions.retrieve.assert_called_with('1')
        self.assertEqual(document, self.prov_document)

    @mock.patch('prov2bigchaindb.core.clients.local_stores.SqliteStore')
    @mock.patch('prov2bigchaindb.core.clients.bd.BigchainDB')
    @mock.patch('prov2bigchaindb.core.clients.accounts.DocumentConceptAccount')
    def test_save_document(self, mock_account, mock_bdb, mock_store):
        mock_account.save_asset.return_value = '1'
        doc_client = clients.DocumentConceptClient(self.account_id, self.host, self.port)
        doc_client.account = mock_account
        doc_client.connection_pool = bdpool.Pool([mock_bdb])

        tx_id = doc_client.save_document(self.prov_document)
        doc_client.account.save_asset.assert_called_with({'prov': self.prov_document.serialize(format='json')},
                                                         mock_bdb)
        self.assertIsInstance(tx_id, str)
        self.assertEqual(tx_id, '1')


class GraphConceptClientTest(unittest.TestCase):
    """Test BigchainDB Base Client"""

    def setUp(self):
        self.account_id = 'Graph_Client_Test'
        self.public_key = 'public'
        self.private_key = 'private'
        self.host = '127.0.0.1'
        self.port = 9984
        self.test_prov_files = setup_test_files()
        self.prov_document = utils.to_prov_document(content=self.test_prov_files["simple"])

    def tearDown(self):
        del self.account_id
        del self.public_key
        del self.private_key
        del self.host
        del self.port
        del self.test_prov_files
        del self.prov_document

    @unittest.skip("testing skipping")
    @mock.patch('prov2bigchaindb.core.clients.local_stores.SqliteStore')
    @mock.patch('prov2bigchaindb.core.clients.clients.bd.BigchainDB')
    @mock.patch('prov2bigchaindb.core.clients.accounts.GraphConceptAccount')
    def test_positive_init(self, mock_account, mock_dbd, mock_store):
        graph_client = clients.GraphConceptClient(self.host, self.port)
        self.assertIsInstance(graph_client, clients.GraphConceptClient)
        # self.assertIsInstance(baseclient.accountstore, utils.LocalAccountStore)
        # self.assertIsInstance(baseclient.account, accounts.DocumentModelAccount)
        self.assertIsInstance(graph_client.node, str)
        self.assertEqual(graph_client.node, 'http://127.0.0.1:9984')

    @unittest.skip("testing skipping")
    @mock.patch('prov2bigchaindb.core.clients.local_stores.SqliteStore')
    @mock.patch('prov2bigchaindb.core.clients.accounts.GraphConceptAccount')
    def test__get_prov_element_list(self, mock_account, mock_bdb):
        graph_client = clients.GraphConceptClient(self.host, self.port)
        prov_document = utils.to_prov_document(content=self.test_prov_files["simple2"])
        prov_records = prov_document.get_records()
        prov_namespaces = prov_document.get_registered_namespaces()
        element_list = clients.GraphConceptClient.calculate_account_data(prov_document)
        for element, relations, namespace in element_list:
            # print(element)
            # print("\twith: ",relations['with_id'])
            # print("\twithout: ",relations['without_id'])
            pass

    @unittest.skip("testing skipping")
    @mock.patch('prov2bigchaindb.core.clients.utils.is_valid_tx')
    @mock.patch('prov2bigchaindb.core.clients.utils.is_block_to_tx_valid')
    @mock.patch('prov2bigchaindb.core.clients.local_stores.SqliteStore')
    @mock.patch('prov2bigchaindb.core.clients.clients.bd.BigchainDB')
    @mock.patch('prov2bigchaindb.core.clients.accounts.GraphConceptAccount')
    def test_get_document(self, mock_account, mock_bdb, mock_store, mock_test_block, mock_test_tx):
        mock_bdb.transactions.retrieve.return_value = {'id': '1', 'asset': {
            'data': {'prov': self.prov_document.serialize(format='json')}}}
        mock_test_block.return_value = True
        mock_test_tx.return_value = True
        graph_client = clients.GraphConceptClient(self.host, self.port)
        graph_client.account = mock_account
        graph_client.connection = mock_bdb
        # Test
        document = graph_client.get_document(['1'])
        sleep(1)
        graph_client.connection.transactions.retrieve.assert_called_with('1')
        self.assertEqual(document, self.prov_document)

    @unittest.skip("testing skipping")
    @mock.patch('prov2bigchaindb.core.clients.local_stores.SqliteStore')
    @mock.patch('prov2bigchaindb.core.clients.clients.bd.BigchainDB')
    @mock.patch('prov2bigchaindb.core.clients.accounts.GraphConceptAccount')
    def test_save_document(self, mock_account, mock_bdb, mock_store):
        mock_account.save_asset.return_value = '1'
        graph_client = clients.GraphConceptClient(self.host, self.port)
        graph_client.account = mock_account
        graph_client.connection = mock_bdb

        tx_id = graph_client.save_document(self.prov_document)
        graph_client.account.save_asset.assert_called_with({'prov': self.prov_document.serialize(format='json')},
                                                           mock_bdb)
        self.assertIsInstance(tx_id, str)
        self.assertEqual(tx_id, '1')


class RoleConceptClientTest(unittest.TestCase):
    """Test BigchainDB Base Client"""

    def setUp(self):
        self.account_id = 'Role_Client_Test'
        self.public_key = 'public'
        self.private_key = 'private'
        self.host = '127.0.0.1'
        self.port = 9984
        self.test_prov_files = setup_test_files()
        self.prov_document = utils.to_prov_document(content=self.test_prov_files["simple"])

    def tearDown(self):
        del self.account_id
        del self.public_key
        del self.private_key
        del self.host
        del self.port
        del self.test_prov_files
        del self.prov_document

    @unittest.skip("testing skipping")
    @mock.patch('prov2bigchaindb.core.clients.local_stores.SqliteStore')
    @mock.patch('prov2bigchaindb.core.clients.clients.bd.BigchainDB')
    @mock.patch('prov2bigchaindb.core.clients.accounts.RoleConceptAccount')
    def test_positive_init(self, mock_account, mock_bdb, mock_store):
        role_client = clients.RoleConceptClient(self.host, self.port)
        self.assertIsInstance(role_client, clients.RoleConceptClient)
        # self.assertIsInstance(baseclient.accountstore, utils.LocalAccountStore)
        # self.assertIsInstance(baseclient.account, accounts.DocumentModelAccount)
        self.assertIsInstance(role_client.node, str)
        self.assertEqual(role_client.node, 'http://127.0.0.1:9984')
        # TODO Check Instance of account_db
        # TODO Check Instance of account

    @unittest.skip("testing skipping")
    @mock.patch('prov2bigchaindb.core.clients.local_stores.SqliteStore')
    @mock.patch('prov2bigchaindb.core.clients.accounts.RoleConceptAccount')
    def test__get_prov_element_list(self, mock_account, moch_bdb):
        role_clien = clients.RoleConceptClient(self.host, self.port)
        prov_document = utils.to_prov_document(content=self.test_prov_files["simple2"])
        prov_records = prov_document.get_records()
        prov_namespaces = prov_document.get_registered_namespaces()
        element_list = clients.RoleConceptClient.calculate_account_data(prov_document)
        for element, relations, namespace in element_list:
            # print(element)
            # print("\twith: ",relations['with_id'])
            # print("\twithout: ",relations['without_id'])
            pass

    @unittest.skip("testing skipping")
    @mock.patch('prov2bigchaindb.core.clients.utils.is_valid_tx')
    @mock.patch('prov2bigchaindb.core.clients.utils.is_block_to_tx_valid')
    @mock.patch('prov2bigchaindb.core.clients.local_stores.SqliteStore')
    @mock.patch('prov2bigchaindb.core.clients.clients.bd.BigchainDB')
    @mock.patch('prov2bigchaindb.core.clients.accounts.RoleConceptAccount')
    def test_get_document(self, mock_account, mock_bdb, mock_store, mock_test_block, mock_test_tx):
        mock_bdb.transactions.retrieve.return_value = {'id': '1', 'asset': {
            'data': {'prov': self.prov_document.serialize(format='json')}}}
        mock_test_block.return_value = True
        mock_test_tx.return_value = True
        role_client = clients.RoleConceptClient(self.host, self.port)
        role_client.account = mock_account
        role_client.connection = mock_bdb
        # Test
        document = role_client.get_document(['1'])
        sleep(1)
        role_client.connection.transactions.retrieve.assert_called_with('1')
        self.assertEqual(document, self.prov_document)

    @unittest.skip("testing skipping")
    @mock.patch('prov2bigchaindb.core.clients.local_stores.SqliteStore')
    @mock.patch('prov2bigchaindb.core.clients.clients.bd.BigchainDB')
    @mock.patch('prov2bigchaindb.core.clients.accounts.RoleConceptAccount')
    def test_save_document(self, mock_account, mock_bdb, mock_store):
        mock_account.save_asset.return_value = '1'
        role_client = clients.RoleConceptClient(self.host, self.port)
        role_client.account = mock_account
        role_client.connection = mock_bdb

        tx_id = role_client.save_document(self.prov_document)
        role_client.account.save_asset.assert_called_with({'prov': self.prov_document.serialize(format='json')},
                                                          mock_bdb)
        self.assertIsInstance(tx_id, str)
        self.assertEqual(tx_id, '1')
