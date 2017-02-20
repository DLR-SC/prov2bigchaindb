import unittest
from . import setup_test_files

from prov2bigchaindb.core import account, utils
from prov2bigchaindb.core.account import BaseAccount, RoleModelAccount, GraphModelAccount, DocumentModelAccount

TEST_DB_FILE = 'test.db'

class BaseAccountTest(unittest.TestCase):

    def setUp(self):
        self.account_db = utils.LocalAccountStore(TEST_DB_FILE)
        self.instance = BaseAccount('Base_Account_Test', self.account_db)

    def tearDown(self):
        del self.instance
        del self.account_db
        import os
        os.remove(TEST_DB_FILE)

class DocumentModelAccountTest(unittest.TestCase):

    def setUp(self):
        self.account_db = utils.LocalAccountStore(TEST_DB_FILE)
        self.instance = DocumentModelAccount('Document_Model_Account_Test', self.account_db)

    def tearDown(self):
        del self.instance
        del self.account_db
        import os
        os.remove(TEST_DB_FILE)
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
