import json
import logging

import random
import requests
import time
from bigchaindb_driver import BigchainDB
from bigchaindb_driver import exceptions as bdb_exceptions
from lxml import etree
from prov import model

from prov2bigchaindb.core import exceptions

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def to_prov_document(content: str or bytes or model.ProvDocument) -> model.ProvDocument:
    """
    Takes a string, bytes or ProvDocument as argument and return a ProvDocument
    The strings or bytes can contain JSON or XML representations of PROV

    :param content: String or BufferedReader or ProvDocument
    :return: ProvDocument
    :rtype: ProvDocument
    """
    if isinstance(content, model.ProvDocument):
        return content

    if isinstance(content, str):
        content_bytes = str.encode(content)
    else:
        content_bytes = content
    try:
        if content_bytes.find(b"{") > -1:
            return model.ProvDocument.deserialize(content=content, format='json').flattened()
        if content_bytes.find(b'<?xml') > -1:
            return model.ProvDocument.deserialize(content=content, format='xml').flattened()
        elif content_bytes.find(b'document') > -1:
            return model.ProvDocument.deserialize(content=content, format='provn').flattened()
        else:
            raise exceptions.ParseException("Invalid PROV Document of type {}".format(type(content)))

    except json.decoder.JSONDecodeError:
        raise exceptions.ParseException("Invalid PROV-JSON of type {}".format(type(content)))
    except etree.XMLSyntaxError:
        raise exceptions.ParseException("Invalid PROV-XML of type {}".format(type(content)))


def wait_until_valid(tx_id: str, bdb_connection: BigchainDB):
    """
    Waits until a transaction is valid in BigchainDB

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
            result = bdb_connection.transactions.status(tx_id)
            if result.get('status') == 'valid':  # others: backlog, undecided
                break
        except bdb_exceptions.NotFoundError:
            time.sleep(1)
            trials += 1
            log.debug("Transaction %s not found in BigchainDB after %s tries out of %s trials", tx_id, trials, trialsmax)
        except bdb_exceptions.TransportError as e:
            trials += 1
            log.debug("Transport Error after %s tries out of %s trials", trials, trialsmax)
            log.debug("%s",e)
    if trials == trialsmax:
        log.error("Transaction id %s not found affer %s tries", tx_id, trialsmax)
        raise exceptions.TransactionIdNotFound(tx_id)


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
    try:
        status = bdb_connection.transactions.status(tx_id).get('status')
    except bdb_exceptions.NotFoundError:
        log.error("Transaction id %s was not found", tx_id)
        raise exceptions.TransactionIdNotFound(tx_id)
    if status == 'valid':
        return True
    log.warning("tx %s is %s", tx_id, status)
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
    node = random.choice(bdb_connection.nodes)
    res = requests.get(node + bdb_connection.blocks.path + '?transaction_id=' + tx_id)
    block_id = res.json()
    if len(block_id) < 1 or len(block_id) > 1:
        raise exceptions.TransactionIdNotFound(tx_id)
    res = requests.get(node + bdb_connection.api_prefix + '/statuses?block_id=' + block_id[0])
    if res.status_code != 200:
        raise exceptions.BlockIdNotFound(block_id[0])
    status = res.json()['status']
    if status == 'valid':
        return True
    return False



