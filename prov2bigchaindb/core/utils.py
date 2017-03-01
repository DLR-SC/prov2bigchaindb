import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from functools import reduce
from io import BufferedReader
import sqlite3

from bigchaindb_driver import exceptions as bdb_exceptions
from prov.model import ProvDocument, six
from prov.graph import prov_to_graph
from prov2bigchaindb.core import exceptions
import requests


def form_string(content):
    """
    Takes a string or BufferedReader as argument and transforms the string into a ProvDocument
    :param content: String or BufferedReader
    :return: ProvDocument
    :rtype: ProvDocument
    """
    if isinstance(content, ProvDocument):
        return content
    elif isinstance(content, BufferedReader):
        content = reduce(lambda total, a: total + a, content.readlines())

    if type(content) is six.binary_type:
        content_str = content[0:15].decode()
        if content_str.find("{") > -1:
            return ProvDocument.deserialize(content=content, format='json').flattened()
        if content_str.find('<?xml') > -1:
            return ProvDocument.deserialize(content=content, format='xml').flattened()
        elif content_str.find('document') > -1:
            return ProvDocument.deserialize(content=content, format='provn').flattened()

    raise exceptions.ParseException("Unsupported input type {}".format(type(content)))

def wait_until_valid(tx_id, bdb_connection):
    trials = 0
    trialsmax = 100
    while trials < trialsmax:
        try:
            if is_valid_tx(tx_id, bdb_connection):
                break
        except bdb_exceptions.NotFoundError as e:
            trials += 1
            log.debug("Wait until transaction is valid: trial %s/%s - %s", trials, trialsmax, tx_id)

def is_valid_tx(tx_id, bdb_connection):
    if bdb_connection.transactions.status(tx_id).get('status') == 'valid':
        return True
    return False

def is_block_to_tx_valid(tx_id, bdb_connection):
    api_url = bdb_connection.info()['_links']['api_v1']
    block_id = requests.get(api_url + 'blocks?tx_id=' + tx_id).json()[0]
    status = requests.get(api_url + 'statuses?block_id=' + block_id).json()['status']
    if status == 'valid':
        return True
    return False

def get_prov_element_list(prov_document):
    namespaces = prov_document.get_registered_namespaces()
    g = prov_to_graph(prov_document=prov_document)
    elements = []
    for node, nodes in g.adjacency_iter():
        relations = {}
        # print(node)
        for n, rel in nodes.items():
            # print("\t", n, rel)
            relations[n] = rel[0]['relation']
        elements.append((node, relations, namespaces))
    return elements


class LocalStore(object):

    def __init__(self, db_name='config.db'):
        self.conn = sqlite3.connect(db_name)
        # Create table
        #with self.conn:
        self.conn.execute('''CREATE TABLE IF NOT EXISTS accounts (account_id text, public_key text, private_key text, tx_id text, PRIMARY KEY (account_id, public_key))''')

    def clean_tables(self):
        with self.conn:
            tables = list(self.conn.execute('''select name from sqlite_master where type is "table"'''))
            self.conn.cursor().executescript(';'.join(["DELETE FROM %s" %i for i in tables]))

    def set_Account(self, account_id, public_key, private_key):
        with self.conn:
            self.conn.execute('INSERT INTO accounts VALUES (?,?,?,?)', (account_id, public_key, private_key, None))

    def get_Account(self, account_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE account_id=?', (account_id,))
        ret = cursor.fetchone()
        return ret

    def set_Tx_Id(self, account_id, tx_id):
        with self.conn:
            self.conn.execute('UPDATE accounts SET tx_id=? WHERE account_id=? ', (tx_id, account_id))

class GraphConceptMetadataStore(LocalStore):
    """"""

    def __init__(self, db_name='config.db'):
        super().__init__(db_name)
        # Create table
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS graph_metadata (tx_id TEXT, public_key TEXT, account_id TEXT, PRIMARY KEY (tx_id, public_key))''')

    def set_Document_MetaData(self, tx_id, public_key, account_id):
        with self.conn:
            self.conn.execute('INSERT INTO graph_metadata VALUES (?,?,?)', (tx_id, public_key, account_id))

    def get_Document_Metadata(self, tx_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM graph_metadata WHERE tx_id=?', (tx_id,))
        ret = cursor.fetchone()
        return ret

class RoleConceptMetadataStore(LocalStore):
    """"""

    def __init__(self,db_name='config.db'):
        super().__init__(db_name)
