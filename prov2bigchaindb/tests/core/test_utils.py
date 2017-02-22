import unittest
from unittest import mock

from prov2bigchaindb.core.utils import LocalStore, LocalAccountStore

TEST_DB_FILE = 'test.db'

class LocalStoreTest(unittest.TestCase):

    def setUp(self):
        self.patcher = mock.patch('prov2bigchaindb.core.utils.sqlite3')
        self.mock_sqlite3 = self.patcher.start()

    def tearDown(self):
        pass

    def test_init(self):
        db = LocalStore(TEST_DB_FILE)
        self.mock_sqlite3.connect.assert_called_with(TEST_DB_FILE)
        db = LocalStore()
        self.mock_sqlite3.connect.assert_called_with('config.db')


class LocalAccountStoreTest(unittest.TestCase):

    def setUp(self):
        self.account_id = 'Local_Test_Account'
        self.public_key = 'public'
        self.private_key = 'private'
        self.patcher = mock.patch('prov2bigchaindb.core.utils.sqlite3')
        self.mock_sqlite3 = self.patcher.start()

    def tearDown(self):
        pass

    def test_init(self):
        db = LocalAccountStore(TEST_DB_FILE)
        self.mock_sqlite3.connect.assert_called_with(TEST_DB_FILE)
        db = LocalAccountStore()
        self.mock_sqlite3.connect.assert_called_with('config.db')
        self.mock_sqlite3.connect().execute.assert_called_with('''CREATE TABLE IF NOT EXISTS accounts (account_id text, public_key text, private_key text, tx_id text, PRIMARY KEY (account_id, public_key))''')

    def test_set_Account(self):
        db = LocalAccountStore()
        db.set_Account(self.account_id, self.public_key, self.private_key)
        self.mock_sqlite3.connect().execute.assert_called_with('INSERT INTO accounts VALUES (?,?,?,?)', (self.account_id, self.public_key, self.private_key, None))


    def test_get_Account(self):
        db = LocalAccountStore()
        db.get_Account(self.account_id)
        self.mock_sqlite3.connect().cursor().execute.assert_called_with('SELECT public_key, private_key, tx_id FROM accounts WHERE account_id=?', (self.account_id,))
