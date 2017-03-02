import logging
from datetime import datetime

from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from prov.model import ProvDocument, ProvElement

from prov2bigchaindb.core import utils, exceptions
from prov2bigchaindb.core.utils import LocalStore

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class BaseAccount(object):
    """ BigchainDB Base Account """

    def __init__(self, account_id: str, store: LocalStore):
        """
        Instantiate BaseAccount object

        :param account_id: Internal id of Account
        :type account_id: str
        :param store: Local database object
        :type store: LocalStore
        """
        assert account_id is not None
        assert store is not None
        self.store = store
        self.account_id = account_id
        self.tx_id = ''
        self.private_key, self.public_key = generate_keypair()
        try:
            self.account_id, self.public_key, self.private_key, self.tx_id = self.store.get_account(self.account_id)
            log.debug("Found account for %s with public_key %s", self.account_id, self.public_key)
        except Exception:
            self.store.write_account(self.account_id, self.public_key, self.private_key)
            log.debug("New account for %s with public_key %s", self.account_id, self.public_key)

    def __str__(self):
        tmp = "{} : {}\n".format(self.account_id, self.public_key)
        return tmp

    def _create_asset(self, bdb_connection: BigchainDB, asset: dict, metadata: dict = None) -> dict:
        """
        Build and send new CREATE transaction

        :param bdb_connection: Connection object for BigchainDB
        :type bdb_connection: BigchainDB
        :param asset: Dictonary with asset data
        :type asset: dict
        :param metadata: Dictonary with additional metadata
        :type metadata: dict or None
        :return: Result with created CREATE transactions
        :rtype: dict
        """
        if metadata is None:
            metadata = {}
        metadata['timestamp'] = datetime.utcnow().timestamp()
        prepared_creation_tx = bdb_connection.transactions.prepare(operation='CREATE',
                                                                   signers=self.public_key,
                                                                   asset=asset,
                                                                   metadata=metadata)
        fulfilled_creation_tx = bdb_connection.transactions.fulfill(prepared_creation_tx,
                                                                    private_keys=self.private_key)
        sent_creation_tx = bdb_connection.transactions.send(fulfilled_creation_tx)
        if fulfilled_creation_tx != sent_creation_tx:
            raise exceptions.CreateRecordException()
        return sent_creation_tx

    def _transfer_asset(self, bdb_connection: BigchainDB, recipient_pub_key: str, tx: dict, metadata: dict = None) -> dict:
        """
        Build and send new TRANSFER transaction

        :param bdb_connection: Connection object for BigchainDB
        :type bdb_connection: BigchainDB
        :param recipient_pub_key: Public key of the recipient
        :type recipient_pub_key: str
        :param tx: Transaction which should be transferd
        :type tx: dict
        :param metadata: Dictionary with additional metadata
        :type metadata: dict or None
        :return: Result with created CREATE transactions
        :rtype: dict
        """
        if metadata is None:
            metadata = {}
        metadata['timestamp'] = datetime.utcnow().timestamp()
        transfer_asset = {'id': tx['id']}
        output_index = 0
        output = tx['outputs'][output_index]
        transfer_input = {
            'fulfillment': output['condition']['details'],
            'fulfills': {
                'output': output_index,
                'txid': tx['id']
            },
            'owners_before': output['public_keys']
        }
        prepared_transfer_tx = bdb_connection.transactions.prepare(
            operation='TRANSFER',
            asset=transfer_asset,
            metadata=metadata,
            inputs=transfer_input,
            recipients=recipient_pub_key
        )
        fulfilled_transfer_tx = bdb_connection.transactions.fulfill(
            prepared_transfer_tx,
            private_keys=self.private_key,
        )
        sent_transfer_tx = bdb_connection.transactions.send(fulfilled_transfer_tx)
        if fulfilled_transfer_tx != sent_transfer_tx:
            raise exceptions.CreateRecordException()
        return sent_transfer_tx

    def get_id(self) -> str:
        """
        Get Account id

        :return: Internal id of Account
        :rtype: str
        """
        return self.account_id

    def get_public_key(self) -> str:
        """
        Get public key

        :return: Public key of Account
        :rtype: str
        """
        return self.public_key


class DocumentConceptAccount(BaseAccount):
    """"""

    def __init__(self, account_id: str, store: LocalStore):
        """
        Instantiate Document Concept Account object

        :param account_id: Internal id of Account
        :type account_id: str
        :param store: Local database object
        :type store: LocalStore
        """
        super().__init__(account_id, store)

    def save_asset(self, asset: dict, bdb_connection: BigchainDB) -> str:
        """
        Writes asset to BigchainDB

        :param asset: Dictonary with asset data
        :type asset: dict
        :param bdb_connection: Connection object for BigchainDB
        :type bdb_connection: BigchainDB
        :return: Transaction Id
        :rtype: str
        """
        asset = {'data': asset}
        metadata = {'account_id': self.account_id}
        tx = self._create_asset(bdb_connection, asset, metadata)
        utils.wait_until_valid(tx['id'], bdb_connection)
        tx = self._transfer_asset(bdb_connection, self.public_key, tx, metadata)
        log.info("Created document: %s - %s", self.account_id, tx['id'])
        return tx['id']


class GraphConceptAccount(BaseAccount):
    """"""

    def __init__(self, prov_element: ProvElement, prov_relations: dict, namespaces: list, store: LocalStore):
        """
        Instantiate Graph Concept Account object

        :param prov_element: ProvElement related to account
        :type prov_element: ProvElement
        :param prov_relations: Dictionary with a outgoing ProvRelations
        :type prov_relations: dict
        :param namespaces: List of Prov Namespaces
        :type namespaces: list
        :param store: Local database object
        :type store: LocalStore
        """
        assert prov_element is not None
        assert prov_relations is not None
        assert namespaces is not None
        self.prov_element = prov_element
        self.prov_namespaces = namespaces
        self.prov_relations = prov_relations
        super().__init__(str(prov_element.identifier), store)

    def get_tx_id(self) -> str:
        """
        Get tx_id that describes the account in BigchainDB

        :return: Transaction id of account
        :rtype: str
        """
        return self.tx_id

    def __str__(self):
        tmp = "{} :\n".format(self.account_id)
        for k, v in self.prov_relations.items():
            tmp = tmp + str(k) + " => " + str(v) + "\n"
        return tmp

    def __create_instance_document(self) -> ProvDocument:
        """
        Builds valid ProvDocument representation of account

        :return: Representation of account as ProvDocument
        :rtype: ProvDocument
        """
        doc = ProvDocument()
        for n in self.prov_namespaces:
            doc.add_namespace(n.prefix, n.uri)
        doc.add_record(self.prov_element)
        return doc

    def __create_relations_document(self) -> (ProvDocument, map):
        """
        Yields ProvDocument and mapping for each relations
        
        :return: Relation as ProvDocument and 
        :rtype: (ProvDocument, map)
        """
        for relation in self.prov_relations:
            doc = ProvDocument()
            mapping = {}
            for relation_type, relation_attr in relation.formal_attributes:
                if relation_attr:
                    recipient = self.store.get_account(str(relation_attr))
                    if recipient:
                        mapping[recipient[0]] = recipient[3]

            for n in self.prov_namespaces:
                doc.add_namespace(n.prefix, n.uri)
            doc.add_record(relation)
            yield doc, mapping

    def save_instance_asset(self, bdb_connection: BigchainDB) -> str:
        """
        Writes instance asset to BigchainDB

        :param bdb_connection: Connection object for BigchainDB
        :type bdb_connection: BigchainDB
        :return: Transactions id of instance
        :rtype: str
        """
        if self.tx_id == '':
            prov_document = self.__create_instance_document()
            asset = {'data': {'prov': prov_document.serialize(format='json')}}
            metadata = {'instance': self.account_id}
            tx = self._create_asset(bdb_connection, asset, metadata)
            utils.wait_until_valid(tx['id'], bdb_connection)
            tx = self._transfer_asset(bdb_connection, self.public_key, tx, metadata)
            self.store.write_tx_id(self.account_id, tx['id'])
            self.tx_id = tx['id']
            log.debug("Created instance: %s - %s", self.account_id, tx['id'])
        return self.tx_id

    def save_relation_assets(self, bdb_connection: BigchainDB) -> list:
        """
        Writes all relation assets to BigchainDB

        :param bdb_connection: Connection object for BigchainDB
        :type bdb_connection: BigchainDB
        :return: Transactions ids of all relations
        :rtype: list
        """
        if self.tx_id == '':
            raise Exception()
        tx_list = []
        for doc, mapping in self.__create_relations_document():
            for records in doc.get_records():
                recipient = self.store.get_account(str(records.args[1]))
                asset = {'data': {'prov': doc.serialize(format='json'), 'map': mapping}}
                metadata = {'relation': '->'.join([self.account_id, recipient[0]])}
                tx = self._create_asset(bdb_connection, asset, metadata)
                utils.wait_until_valid(tx['id'], bdb_connection)
                metadata = {'relation': '->'.join([self.account_id, recipient[0]])}
                tx = self._transfer_asset(bdb_connection, recipient[1], tx, metadata)
                tx_list.append(tx['id'])
                log.debug("Created relation: %s -> %s - %s", self.account_id, recipient[0], tx['id'])
        return tx_list

#
# class RoleConceptAccount(BaseAccount):
#     """"""
#     def __init__(self, account_id, prov_relations, namespaces, account_db):
#         super().__init__(account_id, account_db)
#         self.txid = None
#         self.prov_relations = prov_relations
#         self.prov_namespaces = namespaces
