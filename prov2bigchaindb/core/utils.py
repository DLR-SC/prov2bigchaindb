import logging
from functools import reduce
from io import BufferedReader

import requests
from bigchaindb_driver import BigchainDB
from bigchaindb_driver import exceptions as bdb_exceptions
from prov.graph import prov_to_graph
from prov.model import ProvDocument, six

from prov2bigchaindb.core import exceptions

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def form_string(content: str or BufferedReader or ProvDocument) -> ProvDocument:
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


def wait_until_valid(tx_id: str, bdb_connection: BigchainDB):
    """
    Waits until a transactionis valid in BigchainDB

    :param tx_id: Id of transaction to wait on
    :type tx_id: str
    :param bdb_connection: Connection object for BigchainDB
    :type bdb_connection: BigchainDB
    """
    #  TODO Raise Exception on invalid
    trials = 0
    trialsmax = 100
    while trials < trialsmax:
        try:
            if bdb_connection.transactions.status(tx_id).get('status') == 'valid':
                break
        except bdb_exceptions.NotFoundError:
            trials += 1
            log.debug("Wait until transaction is valid: trial %s/%s - %s", trials, trialsmax, tx_id)


def is_valid_tx(tx_id: str, bdb_connection: BigchainDB) -> bool:
    """
    Checks once if a transaction is valid

    :param tx_id: Id of transaction to check
    :type tx_id: str
    :param bdb_connection: Connection object for BigchainDB
    :type bdb_connection: BigchainDB
    :return: True if valid
    :rtype: bool
    """
    status = bdb_connection.transactions.status(tx_id).get('status')
    if status == 'valid':
        return True
    log.error("tx %s is %s", tx_id, status)
    return False


def is_block_to_tx_valid(tx_id: str, bdb_connection: BigchainDB) -> bool:
    """
    Checks if block with transaction is valid

    :param tx_id: Id of transaction which should be included in the
    :type tx_id: str
    :param bdb_connection: Connection object for BigchainDB
    :type bdb_connection: BigchainDB
    :return: True if transactions is in block and block is valid
    :rtype: bool
    """
    api_url = bdb_connection.info()['_links']['api_v1']
    block_id = requests.get(api_url + 'blocks?tx_id=' + tx_id).json()[0]
    status = requests.get(api_url + 'statuses?block_id=' + block_id).json()['status']
    if status == 'valid':
        return True
    log.error("Block %s is %s", block_id, status)
    return False


def get_prov_element_list(prov_document: ProvDocument) -> list:
    """
    Transforms a ProvDocument into a tuple including ProvElement, list of ProvRelation and list of Namespaces

    :param prov_document: Document to transform
    :type prov_document:
    :return:
    :rtype: list
    """
    namespaces = prov_document.get_registered_namespaces()
    g = prov_to_graph(prov_document=prov_document)
    elements = []
    for node, nodes in g.adjacency_iter():
        relations = []
        for n, tmp_relations in nodes.items():
            for relation in tmp_relations.values():
                relations.append(relation['relation'])
        elements.append((node, relations, namespaces))
    return elements
