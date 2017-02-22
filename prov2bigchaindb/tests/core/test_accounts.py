import unittest
from unittest import mock

import bigchaindb_driver

from prov2bigchaindb.core import exceptions
from . import setup_test_files

from prov2bigchaindb.core import accounts, utils

TEST_DB_FILE = 'test.db'


class BaseAccountTest(unittest.TestCase):

    def setUp(self):
        self.account_id = 'Base_Account_Test'
        self.public_key = 'public'
        self.private_key = 'private'

        self.account_negative_db = mock.Mock(spec=utils.BaseStore, account_id=self.account_id)
        self.account_positive_db = mock.Mock(spec=utils.LocalAccountStore,
                                             db_name=TEST_DB_FILE,
                                             account_id=self.account_id,
                                             **{'get_Account.return_value':(self.public_key,
                                                               self.private_key,
                                                               None
                                                               )
                                                }
                                             )

    def tearDown(self):
        pass

    def test_positive_init_BaseAccount(self):
        account = accounts.BaseAccount(self.account_id, self.account_positive_db)
        self.assertIsInstance(account, accounts.BaseAccount)
        self.assertIsInstance(self.account_positive_db, utils.LocalAccountStore)
        self.assertIsInstance(account.account_id, str)
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
        with self.assertRaises(AssertionError):
            accounts.BaseAccount(None, self.account_positive_db)
        with self.assertRaises(AssertionError):
            accounts.BaseAccount(None, None)
        with self.assertRaises(AssertionError):
            accounts.BaseAccount(self.account_id, self.account_negative_db)

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
        self.account_id = 'Document_Model_Account_Test'
        self.public_key = 'public'
        self.private_key = 'private'
        self.account_db = mock.Mock(spec=utils.LocalAccountStore,
                                             db_name=TEST_DB_FILE,
                                             account_id=self.account_id,
                                             **{'get_Account.return_value':(
                                                 self.public_key,
                                                 self.private_key,
                                                 None)
                                                }
                                             )
        self.bdb_connection = mock.Mock(spec=bigchaindb_driver.BigchainDB,
                                             **{'transactions.retrieve.return_value':'1',
                                                'transactions.prepare.return_value': {'id':'1'},
                                                'transactions.fulfill.return_value': {'id':'1'},
                                                'transactions.send.return_value': {'id':'1'},
                                                }
                                             )

    def tearDown(self):
        pass

    @mock.patch('prov2bigchaindb.core.utils.wait_until_valid')
    def test_positive_save_Asset(self, mock_wait):
        asset = {'data': {'prov': ''}}
        account = accounts.DocumentConceptAccount(self.account_id, self.account_db)
        tx_id = account.save_Asset(asset, self.bdb_connection)
        self.bdb_connection.transactions.prepare.assert_called_with(operation='CREATE', signers=self.public_key, asset=asset, metadata={'account_id':self.account_id})
        self.bdb_connection.transactions.fulfill.assert_called_with({'id':'1'}, private_keys=self.private_key)
        self.bdb_connection.transactions.send.assert_called_with({'id':'1'})
        self.assertEqual(tx_id, '1')

    @mock.patch('prov2bigchaindb.core.utils.wait_until_valid')
    def test_negative_save_Asset(self, mock_wait):
        asset = {'data': {'prov': ''}}
        account = accounts.DocumentConceptAccount(self.account_id, self.account_db)
        self.bdb_connection.configure_mock(**{'transactions.retrieve.return_value':'1',
                                                   'transactions.prepare.return_value': {'id':'1'},
                                                   'transactions.fulfill.return_value': {'id': '1'},
                                                   'transactions.send.return_value': {'id':'2'},
                                                   })
        with self.assertRaises(exceptions.CreateRecordException):
            tx_id = account.save_Asset(asset, self.bdb_connection)
        self.bdb_connection.transactions.prepare.assert_called_with(operation='CREATE', signers=self.public_key, asset=asset, metadata={'account_id':self.account_id})
        self.bdb_connection.transactions.fulfill.assert_called_with({'id':'1'}, private_keys=self.private_key)
        self.bdb_connection.transactions.send.assert_called_with({'id':'1'})

    def test_positive_get_Asset(self):
        account = accounts.DocumentConceptAccount(self.account_id, self.account_db)
        tx_id = account.query_Asset(1, self.bdb_connection)
        self.bdb_connection.transactions.retrieve.assert_called_with(1)
        self.assertEqual(tx_id,'1')

#
#
# class GraphModelAccountTest(unittest.TestCase):
#
#     def setUp(self):
#         self.account_db = utils.LocalAccountStore(TEST_DB_FILE)
#         self.instance = GraphModelAccount('Graph_Model_Account_Test', {}, {},self.account_db)
#
#     def tearDown(self):
#         import os
#         os.remove(TEST_DB_FILE)
#         del self.instance
#         del self.account_db
#
#
# class RoleModelAccountTest(unittest.TestCase):
#
#     def setUp(self):
#         self.account_db = utils.LocalAccountStore(TEST_DB_FILE)
#         self.instance = RoleModelAccount('Role_Model_Account_Test', {}, {}, self.account_db)
#
#     def tearDown(self):
#         import os
#         os.remove(TEST_DB_FILE)
#         del self.instance
#         del self.account_db
