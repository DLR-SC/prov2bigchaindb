import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

import unittest
from unittest import mock
from . import setup_test_files
import bigchaindb_driver

from prov2bigchaindb.core.accounts import GraphConceptAccount
from prov2bigchaindb.core import accounts, utils, exceptions

TEST_DB_FILE = 'test.db'


class BaseAccountTest(unittest.TestCase):

    def setUp(self):
        self.account_id = 'Base_Account_Test'
        self.public_key = 'public'
        self.private_key = 'private'

        self.account_positive_db = mock.Mock(spec=utils.LocalStore,
                                             db_name=TEST_DB_FILE,
                                             account_id=self.account_id,
                                             **{'get_Account.return_value':(self.account_id,
                                                                            self.public_key,
                                                                            self.private_key,
                                                                            None)}
                                             )

    def tearDown(self):
        del self.account_id
        del self.public_key
        del self.private_key
        del self.account_positive_db

    def test_positive_init_BaseAccount(self):
        account = accounts.BaseAccount(self.account_id, self.account_positive_db)
        self.assertIsInstance(account, accounts.BaseAccount)
        self.assertIsInstance(account.public_key, str)
        self.assertIsInstance(account.private_key, str)
        self.assertEqual(account.get_Public_Key(), self.public_key)

    def test_positive_init_without_Account(self):
        self.account_positive_db.configure_mock(**{'get_Account.return_value': None})
        account = accounts.BaseAccount(self.account_id, self.account_positive_db)
        self.assertNotEqual(account.get_Public_Key(), self.public_key)

    def test_negative_init_BaseAccount(self):
        with self.assertRaises(AssertionError):
            accounts.BaseAccount(self.account_id, None)

    def test_positive_get_Id(self):
        account = accounts.BaseAccount(self.account_id, self.account_positive_db)
        self.assertIsInstance(account.get_Id(), str)
        self.assertEqual(account.get_Id(), self.account_id)

    def test_positive_get_Public_Key(self):
        account = accounts.BaseAccount(self.account_id, self.account_positive_db)
        self.assertIsInstance(account.get_Public_Key(), str)
        self.assertEqual(account.get_Public_Key(), self.public_key)


class DocumentConceptAccountTest(unittest.TestCase):

    def setUp(self):
        self.account_id = 'Document_Concept_Account_Test'
        self.public_key = 'public'
        self.private_key = 'private'
        self.account_db = mock.Mock(spec=utils.LocalStore,
                                             db_name=TEST_DB_FILE,
                                             account_id=self.account_id,
                                             **{'get_Account.return_value':(
                                                 self.account_id,
                                                 self.public_key,
                                                 self.private_key,
                                                 None)
                                                }
                                             )
        self.bdb_connection = mock.Mock(spec=bigchaindb_driver.BigchainDB,
                                             **{'transactions.retrieve.return_value':{'id':'1','asset':{'data':{'prov':'1'}}},
                                                'transactions.prepare.return_value': {'id':'1','asset':{'data':{'prov':'1'}}},
                                                'transactions.fulfill.return_value': {'id':'1','asset':{'data':{'prov':'1'}}},
                                                'transactions.send.return_value': {'id':'1','asset':{'data':{'prov':'1'}}},
                                                }
                                             )

    def tearDown(self):
        del self.account_id
        del self.public_key
        del self.private_key
        del self.account_db
        del self.bdb_connection

    @mock.patch('prov2bigchaindb.core.utils.wait_until_valid')
    def test_positive_save_Asset(self, mock_wait):
        asset = {'data': {'prov': ''}}
        account = accounts.DocumentConceptAccount(self.account_id, self.account_db)
        tx_id = account.save_Asset(asset, self.bdb_connection)
        #self.bdb_connection.transactions.prepare.assert_called_with(operation='CREATE', signers=self.public_key, asset={'data':asset}, metadata={'account_id':self.account_id})
        self.bdb_connection.transactions.fulfill.assert_called_with({'id':'1','asset':{'data':{'prov':'1'}}}, private_keys=self.private_key)
        self.bdb_connection.transactions.send.assert_called_with({'id':'1','asset':{'data':{'prov':'1'}}})
        self.assertEqual(tx_id, '1')

    @mock.patch('prov2bigchaindb.core.utils.wait_until_valid')
    def test_negative_save_Asset(self, mock_wait):
        asset = {'data': {'prov': ''}}
        account = accounts.DocumentConceptAccount(self.account_id, self.account_db)
        self.bdb_connection.configure_mock(**{'transactions.retrieve.return_value':{'id':'1','asset':{'data':{'prov':'1'}}},
                                              'transactions.prepare.return_value': {'id':'1','asset':{'data':{'prov':'1'}}},
                                              'transactions.fulfill.return_value': {'id': '1','asset':{'data':{'prov':'1'}}},
                                              'transactions.send.return_value': {'id':'2','asset':{'data':{'prov':'2'}}},
                                              })
        with self.assertRaises(exceptions.CreateRecordException):
            account.save_Asset(asset, self.bdb_connection)
        #self.bdb_connection.transactions.prepare.assert_called_with(operation='CREATE', signers=self.public_key, asset={'data':asset}, metadata={'account_id':self.account_id})
        self.bdb_connection.transactions.fulfill.assert_called_with({'id':'1','asset':{'data':{'prov':'1'}}}, private_keys=self.private_key)
        self.bdb_connection.transactions.send.assert_called_with({'id':'1','asset':{'data':{'prov':'1'}}})

class GraphConceptAccountTest(unittest.TestCase):

    def setUp(self):
        self.test_prov_files = setup_test_files()
        self.prov_document = utils.form_string(content=self.test_prov_files["simple"])
        self.prov_element, self.prov_relations, self.prov_namespaces = utils.get_prov_element_list(self.prov_document)[0]
        self.public_key = 'public'
        self.private_key = 'private'
        self.store = mock.Mock(spec=utils.LocalStore,
                                    db_name=TEST_DB_FILE,
                                    account_id=self.prov_element,
                                    **{'get_Account.return_value':(
                                                 self.public_key,
                                                 self.private_key,
                                                 None)
                                                }
                                    )
        self.bdb_connection = mock.Mock(spec=bigchaindb_driver.BigchainDB,
                                        **{'transactions.retrieve.return_value': {'id':'1','asset':{'data':{'prov':'1'}}},
                                           'transactions.prepare.return_value': {'id': '1','asset':{'data':{'prov':'1'}}},
                                           'transactions.fulfill.return_value': {'id': '1','asset':{'data':{'prov':'1'}}},
                                           'transactions.send.return_value': {'id': '1','asset':{'data':{'prov':'1'}}},
                                           }
                                        )

    def tearDown(self):
        del self.prov_document
        del self.prov_element
        del self.prov_relations
        del self.prov_namespaces
        del self.public_key
        del self.private_key
        del self.store
        del self.bdb_connection
        [self.test_prov_files[k].close() for k in self.test_prov_files.keys()]
        del self.test_prov_files

    def test_positive_init_without_Account(self):
        self.store.configure_mock(**{'get_Account.return_value': None})
        account = accounts.GraphConceptAccount(self.prov_element, self.prov_relations, self.prov_namespaces, self.store)
        self.assertNotEqual(account.get_Public_Key(), self.public_key)
        self.assertEqual(account.tx_id, None)
        self.assertEqual(account.prov_namespaces, self.prov_namespaces)
        self.assertEqual(account.prov_relations, self.prov_relations)

    @unittest.skip("testing skipping")
    def test__create_instance(self):
        raise NotImplementedError()

    @unittest.skip("testing skipping")
    def test__create_relations(self):
        raise NotImplementedError()

    @mock.patch('prov2bigchaindb.core.utils.wait_until_valid')
    def test_positiv_save_Class_Asset(self, mock_wait):
        self.store.configure_mock(**{'get_Account.return_value': None})
        account = accounts.GraphConceptAccount(self.prov_element, self.prov_relations, self.prov_namespaces, self.store)
        tx_id = account.save_Instance_Asset(self.bdb_connection)
        asset = {'data': {'prov': account._create_instance_document().serialize(format='json')}}
        #self.bdb_connection.transactions.prepare.assert_called_with(operation='CREATE', signers=account.public_key, asset=asset, metadata={'account_id':str(self.prov_element.identifier)})
        self.bdb_connection.transactions.fulfill.assert_called_with({'id':'1','asset':{'data':{'prov':'1'}}}, private_keys=account.private_key)
        self.bdb_connection.transactions.send.assert_called_with({'id':'1','asset':{'data':{'prov':'1'}}})
        self.assertEqual(tx_id, '1')
        self.assertEqual(account.tx_id, '1')

    @mock.patch('prov2bigchaindb.core.utils.wait_until_valid')
    def test_negativ_save_Class_Asset(self, mock_wait):
        self.store.configure_mock(**{'get_Account.return_value': None})
        account = accounts.GraphConceptAccount(self.prov_element, self.prov_relations, self.prov_namespaces, self.store)
        self.bdb_connection.configure_mock(**{'transactions.retrieve.return_value': {'id':'1','asset':{'data':{'prov':'1'}}},
                                                   'transactions.prepare.return_value': {'id':'1','asset':{'data':{'prov':'1'}}},
                                                   'transactions.fulfill.return_value': {'id': '1','asset':{'data':{'prov':'1'}}},
                                                   'transactions.send.return_value': {'id':'2','asset':{'data':{'prov':'2'}}},
                                                   })
        asset = {'data': {'prov': account._create_instance_document().serialize(format='json')}}
        with self.assertRaises(exceptions.CreateRecordException):
            account.save_Instance_Asset(self.bdb_connection)
        #self.bdb_connection.transactions.prepare.assert_called_with(operation='CREATE', signers=account.public_key, asset=asset, metadata={'account_id':str(self.prov_element.identifier)})
        self.bdb_connection.transactions.fulfill.assert_called_with({'id':'1','asset':{'data':{'prov':'1'}}}, private_keys=account.private_key)
        self.bdb_connection.transactions.send.assert_called_with({'id':'1','asset':{'data':{'prov':'1'}}})
        self.assertEqual(account.tx_id, None)

    @unittest.skip("testing skipping")
    def test_save_Relations_Assets(self):
        raise NotImplementedError()

# class RoleModelAccountTest(unittest.TestCase):
#
#     def setUp(self):
#         self.account_db = utils.LocalAccountStore(TEST_DB_FILE)
#         self.instance = RoleModelAccount('Role_Model_Account_Test', {}, {}, self.account_db)
#
#     def tearDown(self):
#         del self.instance
#         del self.account_db
