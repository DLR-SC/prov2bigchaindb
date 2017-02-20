import unittest
from prov2bigchaindb.core.account import BaseAccount


class KeyStoreTest(unittest.TestCase):

    def setUp(self):
        self.instance = BaseAccount()

    def tearDown(self):
        del self.instance
