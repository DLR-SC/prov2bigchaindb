import logging

import sqlite3
from prov2bigchaindb.core import exceptions

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class BaseStore(object):
    def __init__(self, db_name: str = None):
        """
        Instantiate BaseStore object

        :param db_name: Name of database
        :type db_name: str
        """
        self.db_name = db_name

    def clean_tables(self):
        """
        Delete all entries from all tables (Used for unit tests)
        """
        raise NotImplementedError("Abstract method")

    def write_account(self, account_id: str, public_key: str, private_key: str, tx_id: str = None):
        """
        Writes a new account entry in to the table accounts

        :param tx_id: Transactions id
        :type tx_id: str
        :param account_id: Id of account
        :type account_id: str
        :param public_key: Public key of account
        :type public_key: str
        :param private_key: Private key of account
        :type private_key: str
        """
        raise NotImplementedError("Abstract method")

    def get_account(self, account_id: str) -> tuple:
        """
        Returns tuple of account from data by account_id

        :param account_id: Id of account
        :type account_id: str
        :return: Tuple with account_id, public_key, private_key and tx_id
        :rtype: tuple
        """
        raise NotImplementedError("Abstract method")

    def write_tx_id(self, account_id: str, tx_id: str):
        """
        Writes tx_id for given account_id

        :param account_id: Id of account
        :type account_id: str
        :param tx_id: Transaction id, which represents the account in BigchainDB
        :type tx_id: str
        """
        raise NotImplementedError("Abstract method")


class SqliteStore(BaseStore):
    def __init__(self, db_name: str = ':memory:'):
        """
        Instantiate LocalStore object for handling the sqlite3 database which stores all accounts (PoC!)

        :param db_name: Name of local database file
        :type db_name: str
        """
        self.conn = sqlite3.connect(db_name)
        # Create table
        self.conn.execute(
            '''CREATE TABLE IF NOT EXISTS accounts (account_id TEXT, public_key TEXT, private_key TEXT, tx_id TEXT, PRIMARY KEY (account_id, public_key))''')
        super().__init__(db_name)

    def clean_tables(self):
        """
        Delete all entries from all tables (Used for unit tests)
        """
        with self.conn:
            tables = list(self.conn.execute('''SELECT name FROM sqlite_master WHERE type IS "table"'''))
            self.conn.cursor().executescript(';'.join(["DELETE FROM %s" % i for i in tables]))

    def write_account(self, account_id: str, public_key: str, private_key: str, tx_id: str = None):
        """
        Writes a new account entry in to the table accounts

        :param tx_id: Transactions id
        :type tx_id: str
        :param account_id: Id of account
        :type account_id: str
        :param public_key: Public key of account
        :type public_key: str
        :param private_key: Private key of account
        :type private_key: str
        """
        with self.conn:
            self.conn.execute('INSERT INTO accounts VALUES (?,?,?,?)', (account_id, public_key, private_key, tx_id))

    def get_account(self, account_id: str) -> tuple:
        """
        Returns tuple of account from data by account_id

        :param account_id: Id of account
        :type account_id: str
        :return: Tuple with account_id, public_key, private_key and tx_id
        :rtype: tuple
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE account_id=?', (account_id,))
        ret = cursor.fetchone()
        if ret is None:
            raise exceptions.NoAccountFoundException("No account with id " + account_id)
        return ret

    def write_tx_id(self, account_id: str, tx_id: str):
        """
        Writes tx_id for given account_id

        :param account_id: Id of account
        :type account_id: str
        :param tx_id: Transaction id, which represents the account in BigchainDB
        :type tx_id: str
        """
        with self.conn:
            self.conn.execute('UPDATE accounts SET tx_id=? WHERE account_id=? ', (tx_id, account_id))
