import logging
import unittest
from unittest import mock
import sqlite3
from prov2bigchaindb.core.utils import LocalStore

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

TEST_DB_FILE = 'test.db'


class LocalStoreTest(unittest.TestCase):
    def setUp(self):
        self.account_id = 'Local_Test_Account'
        self.public_key = 'public'
        self.private_key = 'private'

    def tearDown(self):
        del self.account_id
        del self.public_key
        del self.private_key

    @mock.patch('prov2bigchaindb.core.utils.sqlite3')
    def test_init(self, mock_sqlite3):
        LocalStore(TEST_DB_FILE)
        mock_sqlite3.connect.assert_called_with(TEST_DB_FILE)
        LocalStore()
        mock_sqlite3.connect.assert_called_with('config.db')
        mock_sqlite3.connect().execute.assert_called_with('''CREATE TABLE IF NOT EXISTS accounts (account_id TEXT, public_key TEXT, private_key TEXT, tx_id TEXT, PRIMARY KEY (account_id, public_key))''')

    @mock.patch('prov2bigchaindb.core.utils.sqlite3')
    def test_set_account(self, mock_sqlite3):
        db = LocalStore()
        db.set_account(self.account_id, self.public_key, self.private_key)
        mock_sqlite3.connect().execute.assert_called_with('INSERT INTO accounts VALUES (?,?,?,?)',
                                                          (self.account_id, self.public_key, self.private_key, None))

    @mock.patch('prov2bigchaindb.core.utils.sqlite3')
    def test_get_account(self, mock_sqlite3):
        db = LocalStore()
        db.get_account(self.account_id)
        mock_sqlite3.connect().cursor().execute.assert_called_with('SELECT * FROM accounts WHERE account_id=?',
                                                                   (self.account_id,))

    def test_live_set_account(self):
        db = LocalStore(TEST_DB_FILE)
        db.clean_tables()
        db.set_account(self.account_id, self.public_key, self.private_key)
        with self.assertRaises(sqlite3.IntegrityError):
            db.set_account(self.account_id, self.public_key, self.private_key)
        db.clean_tables()

    def test_live_get_account(self):
        db = LocalStore(TEST_DB_FILE)
        db.clean_tables()
        db.set_account(self.account_id, self.public_key, self.private_key)
        account_id, pub, priv, tx_id = db.get_account(self.account_id)
        self.assertEqual(account_id, self.account_id)
        self.assertEqual(pub, self.public_key)
        self.assertEqual(priv, self.private_key)
        self.assertEqual(tx_id, None)
        ret = db.get_account('wrong_id')
        self.assertEqual(ret, None)
        db.clean_tables()