import unittest
from prov2bigchaindb.core.utils import LocalStore, LocalAccountStore

TEST_DB_FILE = 'test.db'

class LocalStoreTest(unittest.TestCase):

    def setUp(self):
        self.instance = LocalStore(TEST_DB_FILE)

    def tearDown(self):
        del self.instance
        import os
        os.remove(TEST_DB_FILE)

class LocalAccountStoreTest(unittest.TestCase):

    def setUp(self):
        self.instance = LocalAccountStore(TEST_DB_FILE)

    def tearDown(self):
        del self.instance
        import os
        os.remove(TEST_DB_FILE)
