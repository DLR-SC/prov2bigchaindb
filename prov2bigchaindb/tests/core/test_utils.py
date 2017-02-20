import unittest
from prov2bigchaindb.core.utils import LocalStore, LocalAccountStore


class UtilTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

class LocalStoreTest(unittest.TestCase):

    def setUp(self):
        self.instance = LocalStore()

    def tearDown(self):
        del self.instance


class LocalAccountStoreTest(unittest.TestCase):

    def setUp(self):
        self.instance = LocalAccountStore()

    def tearDown(self):
        del self.instance