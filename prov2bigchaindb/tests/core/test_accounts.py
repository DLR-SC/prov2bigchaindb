import unittest
from . import setup_test_files

from prov2bigchaindb.core import accounts, utils

TEST_DB_FILE = 'test.db'

class BaseAccountTest(unittest.TestCase):

    def setUp(self):
        self.test_id = 'Base_Account_Test'
        self.account_db = utils.LocalAccountStore(TEST_DB_FILE)

    def tearDown(self):
        del self.account_db
        import os
        os.remove(TEST_DB_FILE)

    def test_positive_BaseAccount(self):
        account = accounts.BaseAccount(self.test_id, self.account_db)
        self.assertIsInstance(account, accounts.BaseAccount)
        self.assertIsInstance(account.account_db, utils.LocalAccountStore)
        self.assertIsInstance(account.account_id, str)
        self.assertIsInstance(account.public_key, str)
        self.assertIsInstance(account.private_key, str)

    def test_negative_BaseAccount(self):
        with self.assertRaises(AssertionError):
            accounts.BaseAccount(self.test_id, None)
        with self.assertRaises(AssertionError):
            accounts.BaseAccount(None, self.account_db)
        with self.assertRaises(AssertionError):
            accounts.BaseAccount(None, None)

    def test_positive_get_Id(self):
        account = accounts.BaseAccount(self.test_id, self.account_db)
        self.assertIsInstance(account.get_Id(), str)
        self.assertEqual(account.account_id, account.get_Id())

    def test_positive_get_Public_Key(self):
        account = accounts.BaseAccount(self.test_id, self.account_db)
        self.assertIsInstance(account.get_Public_Key(), str)
        self.assertEqual(account.public_key, account.get_Public_Key())


class DocumentModelAccountTest(unittest.TestCase):

    def setUp(self):
        self.test_id = 'Document_Model_Account_Test'
        self.account_db = utils.LocalAccountStore(TEST_DB_FILE)

    def tearDown(self):
        del self.account_db
        import os
        os.remove(TEST_DB_FILE)

    def test_positive_DocumentModelAccount(self):
        account = accounts.BaseAccount(self.test_id, self.account_db)
        self.assertIsInstance(account, accounts.BaseAccount)
        self.assertIsInstance(account.account_db, utils.LocalAccountStore)
        self.assertIsInstance(account.account_id, str)
        self.assertIsInstance(account.public_key, str)
        self.assertIsInstance(account.private_key, str)

    def test_negative_DocumentModelAccount(self):
        with self.assertRaises(AssertionError):
            accounts.BaseAccount(self.test_id, None)
        with self.assertRaises(AssertionError):
            accounts.BaseAccount(None, self.account_db)
        with self.assertRaises(AssertionError):
            accounts.BaseAccount(None, None)

    def test_positive_get_Id(self):
        account = accounts.BaseAccount(self.test_id, self.account_db)
        self.assertIsInstance(account.get_Id(), str)
        self.assertEqual(account.account_id, account.get_Id())

    def test_positive_get_Public_Key(self):
        account = accounts.BaseAccount(self.test_id, self.account_db)
        self.assertIsInstance(account.get_Public_Key(), str)
        self.assertEqual(account.public_key, account.get_Public_Key())

    @unittest.skip("testing skipping")
    def test_positive_save_Asset(self):
        raise NotImplementedError()

    @unittest.skip("testing skipping")
    def test_positive_get_Asset(self):
        raise NotImplementedError()


    @unittest.skip("testing skipping")
    def test_negative_save_asset(self):
        raise NotImplementedError()

    @unittest.skip("testing skipping")
    def test_negative_get_asset(self):
        raise NotImplementedError()

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
