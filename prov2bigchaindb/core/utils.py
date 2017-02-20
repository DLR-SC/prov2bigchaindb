from functools import reduce
from io import BufferedReader
import pkg_resources
import sqlite3

from prov.model import ProvDocument, six

from prov2bigchaindb.core.exceptions import ParseException


def form_string(content):
    """
    Take a string or BufferedReader as argument and transform the string into a ProvDocument
    :param content: Takes a sting or BufferedReader
    :return: ProvDocument
    """
    if isinstance(content, ProvDocument):
        return content
    elif isinstance(content, BufferedReader):
        content = reduce(lambda total, a: total + a, content.readlines())

    if type(content) is six.binary_type:
        content_str = content[0:15].decode()
        if content_str.find("{") > -1:
            return ProvDocument.deserialize(content=content, format='json')
        if content_str.find('<?xml') > -1:
            return ProvDocument.deserialize(content=content, format='xml')
        elif content_str.find('document') > -1:
            return ProvDocument.deserialize(content=content, format='provn')

    raise ParseException("Unsupported input type {}".format(type(content)))


def setup_test_files():
    test_resources = {
        'simple': {'package': 'prov2bigchaindb', 'file': '/assets/example-abstract.json'},
        'quantified': {'package': 'prov2bigchaindb', 'file': '/assets/quantified-self.json'},
        'thesis': {'package': 'prov2bigchaindb', 'file': '/assets/thesis-example-full.json'}
    }
    return dict((key, pkg_resources.resource_stream(val['package'], val['file'])) for key, val in test_resources.items())



class LocalStore(object):
    def __init__(self, db_name='config.db'):
        self.conn = sqlite3.connect(db_name)


class LocalAccountStore(LocalStore):
    def __init__(self, db_name='config.db'):
        super().__init__(db_name)
        # Create table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS accounts (account_id text, public_key text, private_key text, tx_id text, PRIMARY KEY (account_id, public_key))''')

    def set_Account(self, account_id, public_key, private_key):
        self.conn.execute('INSERT INTO accounts VALUES (?,?,?,?)', (account_id, public_key, private_key, None))
        self.conn.commit()

    def get_Account(self, account_id):
        return self.conn.execute('SELECT * FROM accounts WHERE account_id=?', (account_id,))


class DocumentTxStore(LocalStore):
    """"""

    def __init__(self, db_name='config.db'):
        super().__init__(db_name)


class GraphTxStore(LocalStore):
    """"""

    def __init__(self, db_name='config.db'):
        super().__init__(db_name)


class RoleTxStore(LocalStore):
    """"""

    def __init__(self,db_name='config.db'):
        super().__init__(db_name)
