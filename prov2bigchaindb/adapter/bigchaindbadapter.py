import json

import bigchaindb_driver

from prov2bigchaindb.exceptions import InvalidOptionsException, CreateRecordException
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.exceptions import NotFoundError
from bigchaindb_driver.crypto import generate_keypair
import logging


log = logging.getLogger(__name__)


class BigchainDBAdapter(object):
    """ Bigchain Database Adapter """

    def __init__(self, host='0.0.0.0', port=9984):
        self.node = 'http://{}:{}'.format(host, str(port))
        self.driver = BigchainDB(self.node)

    def save(self, attributes, metadata, public_key, private_key):
        """
        Saves a entity, activity or entity into the database

        :param attributes: Attributes as dict for the record. Be careful you have to encode the dict
        :type attributes: dict
        :param metadata: Metadata as dict for the record. Be careful you have to encode the dict but you can be sure that all meta keys are always there
        :type metadata: dict
        :return: Record id
        :rtype: str
        """
        asset={'data':{'prov':attributes, 'map':metadata}}
        prepared_creation_tx = self.driver.transactions.prepare(operation='CREATE', signers=public_key, asset=asset, metadata=metadata)
        #print(prepared_creation_tx)
        fulfilled_creation_tx = self.driver.transactions.fulfill(prepared_creation_tx, private_keys=private_key)
        sent_creation_tx = self.driver.transactions.send(fulfilled_creation_tx)

        if fulfilled_creation_tx != sent_creation_tx:
            raise CreateRecordException()
        trials = 0
        while trials < 100:
            try:
                if self.driver.transactions.status(sent_creation_tx['id']).get('status') == 'valid':
                    break
            except NotFoundError:
                trials += 1
        return sent_creation_tx['id']

    def transfer(self, attributes, metadata, public_key, private_key):
        """
        Create a relation between 2 nodes

        :param from_node: The identifier
        :type from_node: str
        :param to_node: The identifier for the destination node
        :type: to_node: str
        :param attributes:  Attributes as dict for the record. Be careful you have to encode the dict
        :type attributes: dict
        :param metadata: Metadata as dict for the record. Be careful you have to encode the dict but you can be sure that all meta keys are always there
        :type metadata: dict
        :return: Record id
        :rtype: str
        """
        raise NotImplementedError("Abstract method")

    def get_record(self, record_id):
        """
        Return a single record

        :param record_id: The id
        :type record_id: str
        :return: DbRecord
        :rtype: DbRecord
        """
        raise NotImplementedError("Abstract method")

    def get_relation(self, relation_id):
        """
        Returns a single relation

        :param relation_id: The id
        :type relation_id: str
        :return: DbRelation
        :rtype: DbRelation
        """
        raise NotImplementedError("Abstract method")
