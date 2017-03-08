import logging
from datetime import datetime

from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from prov.model import ProvDocument, ProvElement

from prov2bigchaindb.core import utils, exceptions, local_stores

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class BaseAccount(object):
    """
    BigchainDB Base Account
    """

    def __init__(self, account_id: str, store: local_stores.BaseStore):
        """
        Instantiate BaseAccount object

        :param account_id: Internal id of Account
        :type account_id: str
        :param store: Local database object
        :type store: local_stores.BaseStore
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
        except exceptions.NoAccountFoundException:
            self.store.write_account(self.account_id, self.public_key, self.private_key)
            log.debug("New account for %s with public_key %s", self.account_id, self.public_key)

    def __str__(self):
        return "{} : {}".format(self.account_id, self.public_key)

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

    def _transfer_asset(self, bdb_connection: BigchainDB, recipient_pub_key: str, tx: dict,
                        metadata: dict = None) -> dict:
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
    """
    BigchainDB Document Concept Account
    """

    def __init__(self, account_id: str, store: local_stores.BaseStore):
        """
        Instantiate Document Concept Account object

        :param account_id: Internal id of Account
        :type account_id: str
        :param store: Local database object
        :type store: local_stores.BaseStore
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
    """
    BigchainDB Graph Concept Account
    """

    def __init__(self, prov_element: ProvElement, prov_relations: dict, id_mapping: dict, namespaces: list,
                 store: local_stores.BaseStore = local_stores.BaseStore()):
        """
        Instantiate Graph Concept Account object

        :param prov_element: ProvElement related to account
        :type prov_element: ProvElement
        :param prov_relations: List including dictionaries of all outgoing ProvRelations
        :type prov_relations: list
        :param namespaces: List of Prov Namespaces
        :type namespaces: list
        :param store: Local database object
        :type store: local_stores.BaseStore
        """
        assert prov_element is not None
        assert prov_relations is not None
        assert namespaces is not None
        self.prov_element = prov_element
        self.prov_namespaces = namespaces
        self.prov_relations_with_id = prov_relations['with_id']
        self.id_mapping = id_mapping
        self.prov_relations_without_id = prov_relations['without_id']
        super().__init__(str(prov_element.identifier), store)

    def get_tx_id(self) -> str:
        """
        Get tx_id that describes the account in BigchainDB

        :return: Transaction id of account
        :rtype: str
        """
        return self.tx_id

    def has_relations_with_id(self) -> bool:
        """
        Indicates whether account has relation with ids
        :return: True if one or more relation does have ids
        :rtype: bool
        """
        return len(self.prov_relations_with_id) != 0

    def has_relations_without_id(self) -> bool:
        """
        Indicates whether account has relation with ids
        :return: True if one or more relation does have ids
        :rtype: bool
        """
        return len(self.prov_relations_without_id) != 0

    def __str__(self):
        return "{} : {}\n\t{}\n\t{}".format(self.account_id, self.public_key, self.prov_relations_with_id,
                                            self.prov_relations_without_id)

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

    def __create_relation(self, relation) -> (ProvDocument, dict):
        """
        Yields ProvDocument and mapping for each relations
        
        :return: Relation as ProvDocument and 
        :rtype: (str, ProvDocument, map)
        """
        doc = ProvDocument()
        mapping = {}
        for relation_type, relation_attr in relation.formal_attributes:
            if relation_attr:
                try:
                    recipient = self.store.get_account(str(relation_attr))
                    mapping[recipient[0]] = recipient[3]
                except exceptions.NoAccountFoundException:
                    try:
                        recipient = self.id_mapping.get(str(relation_attr))
                        mapping[str(relation_attr)] = recipient
                    except exceptions.NoRelationFoundException:
                        log.info("Found no tx for %s", relation_attr)

        for n in self.prov_namespaces:
            doc.add_namespace(n.prefix, n.uri)
        doc.add_record(relation)
        yield (doc, mapping)

    def save_relations_with_ids(self, bdb_connection: BigchainDB) -> list:
        """
        Writes all relation assets to BigchainDB

        :param bdb_connection: Connection object for BigchainDB
        :type bdb_connection: BigchainDB
        :return: Transactions ids of all relations
        :rtype: list
        """
        if self.tx_id == '':
            raise exceptions.AccountNotCreatedException("Account must be created before transactions")
        tx_list = []
        for relation in self.prov_relations_with_id:
            for doc, mapping in self.__create_relation(relation):
                for record in doc.get_records():
                    recipient = self.store.get_account(str(record.args[1]))
                    asset = {'data': {'prov': doc.serialize(format='json'), 'map': mapping}}
                    metadata = {'relation': '->'.join([self.account_id, recipient[0]])}
                    tx = self._create_asset(bdb_connection, asset, metadata)
                    utils.wait_until_valid(tx['id'], bdb_connection)
                    metadata = {'relation': str(record.identifier) + " - " + '->'.join([self.account_id, recipient[0]])}
                    tx = self._transfer_asset(bdb_connection, recipient[1], tx, metadata)
                    tx_list.append(tx['id'])
                    self.id_mapping[str(record.identifier)] = tx['id']
                    log.debug("Created relation %s: %s -> %s - %s", record.identifier, self.account_id, recipient[0],
                              tx['id'])
        return tx_list

    def save_relations_without_ids(self, bdb_connection: BigchainDB) -> list:
        """
        Writes all relation assets to BigchainDB

        :param bdb_connection: Connection object for BigchainDB
        :type bdb_connection: BigchainDB
        :return: Transactions ids of all relations
        :rtype: list
        """
        if self.tx_id == '':
            raise exceptions.AccountNotCreatedException("Account must be created before transactions")
        tx_list = []
        for relation in self.prov_relations_without_id:
            for doc, mapping in self.__create_relation(relation):
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


class RoleConceptAccount(BaseAccount):
    """
    BigchainDB Graph Concept Account
    """

    def __init__(self, prov_element: ProvElement, elements: dict, id_mapping: dict, namespaces: list,
                 store: local_stores.BaseStore = local_stores.BaseStore()):
        """
        Instantiate Graph Concept Account object

        :param prov_element: ProvElement related to account
        :type prov_element: ProvElement
        :param namespaces: List of Prov Namespaces
        :type namespaces: list
        :param store: Local database object
        :type store: local_stores.BaseStore
        """
        assert prov_element is not None
        assert elements is not None
        assert namespaces is not None
        self.prov_element = prov_element
        self.prov_namespaces = namespaces
        self.prov_elements_with_id = elements['with_id']
        self.prov_elements_without_id = elements['without_id']
        self.id_mapping = id_mapping

        super().__init__(str(prov_element.identifier), store)

    def get_tx_id(self) -> str:
        """
        Get tx_id that describes the account in BigchainDB

        :return: Transaction id of account
        :rtype: str
        """
        return self.tx_id

    def has_relations_with_id(self) -> bool:
        """
        Indicates whether account has relation with ids
        :return: True if one or more relation does have ids
        :rtype: bool
        """
        return len(self.prov_relations_with_id) != 0

    def has_relations_without_id(self) -> bool:
        """
        Indicates whether account has relation with ids
        :return: True if one or more relation does have ids
        :rtype: bool
        """
        return len(self.prov_relations_without_id) != 0

    def __str__(self):
        return "{} : {}\n\t{}\n\t{}".format(self.account_id, self.public_key, self.prov_relations_with_id,
                                            self.prov_relations_without_id)

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

    def __create_relation(self, relation) -> (ProvDocument, dict):
        """
        Yields ProvDocument and mapping for each relations

        :return: Relation as ProvDocument and
        :rtype: (str, ProvDocument, map)
        """
        doc = ProvDocument()
        mapping = {}
        relation = relation
        for relation_type, relation_attr in relation.formal_attributes:
            if relation_attr:
                try:
                    recipient = self.store.get_account(str(relation_attr))
                    mapping[recipient[0]] = recipient[3]
                except exceptions.NoAccountFoundException:
                    try:
                        recipient = self.id_mapping.get(str(relation_attr))
                        mapping[str(relation_attr)] = recipient
                    except exceptions.NoRelationFoundException:
                        log.info("Found no tx for %s", relation_attr)

        for n in self.prov_namespaces:
            doc.add_namespace(n.prefix, n.uri)
        doc.add_record(relation)
        yield (doc, mapping)

    def save_relations_with_ids(self, bdb_connection: BigchainDB) -> list:
        """
        Writes all relation assets to BigchainDB

        :param bdb_connection: Connection object for BigchainDB
        :type bdb_connection: BigchainDB
        :return: Transactions ids of all relations
        :rtype: list
        """
        if self.tx_id == '':
            raise exceptions.AccountNotCreatedException("Account must be created before transactions")
        tx_list = []
        for relation in self.prov_relations_with_id:
            for doc, mapping in self.__create_relation(relation):
                for record in doc.get_records():
                    recipient = self.store.get_account(str(record.args[1]))
                    asset = {'data': {'prov': doc.serialize(format='json'), 'map': mapping}}
                    metadata = {'relation': '->'.join([self.account_id, recipient[0]])}
                    tx = self._create_asset(bdb_connection, asset, metadata)
                    utils.wait_until_valid(tx['id'], bdb_connection)
                    metadata = {'relation': str(record.identifier) + " - " + '->'.join([self.account_id, recipient[0]])}
                    tx = self._transfer_asset(bdb_connection, recipient[1], tx, metadata)
                    tx_list.append(tx['id'])
                    self.id_mapping[str(record.identifier)] = tx['id']
                    log.debug("Created relation %s: %s -> %s - %s", record.identifier, self.account_id, recipient[0],
                              tx['id'])
        return tx_list

    def save_relations_without_ids(self, bdb_connection: BigchainDB) -> list:
        """
        Writes all relation assets to BigchainDB

        :param bdb_connection: Connection object for BigchainDB
        :type bdb_connection: BigchainDB
        :return: Transactions ids of all relations
        :rtype: list
        """
        if self.tx_id == '':
            raise exceptions.AccountNotCreatedException("Account must be created before transactions")
        tx_list = []
        for relation in self.prov_relations_without_id:
            for doc, mapping in self.__create_relation(relation):
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
