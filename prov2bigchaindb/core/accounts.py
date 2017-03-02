import logging
from prov.model import ProvDocument
from bigchaindb_driver.crypto import generate_keypair
from prov2bigchaindb.core import utils, exceptions
from datetime import datetime

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class BaseAccount(object):
    """ BigchainDB Base Account """

    def __init__(self, account_id, store):
        assert account_id is not None
        assert store is not None
        self.store = store
        self.account_id = account_id
        self.tx_id = None
        self.private_key, self.public_key = generate_keypair()
        try:
            self.account_id, self.public_key, self.private_key, self.tx_id = self.store.get_account(self.account_id)
            log.debug("Found account for %s with public_key %s", self.account_id, self.public_key)
        except Exception:
            self.store.set_account(self.account_id, self.public_key, self.private_key)
            log.debug("New account for %s with public_key %s", self.account_id, self.public_key)

    def __str__(self):
        tmp = "{} : {}\n".format(self.account_id, self.public_key)
        return tmp

    def _create_asset(self, bdb_connection, asset, metadata=None):
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

    def _transfer_asset(self, bdb_connection, recipient_pub_key, tx, metadata=None):
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

    def get_id(self):
        return self.account_id

    def get_public_key(self):
        return self.public_key


class DocumentConceptAccount(BaseAccount):
    """"""

    def __init__(self, account_id, store):
        super().__init__(account_id, store)

    def save_asset(self, asset, bdb_connection):
        asset = {'data': asset}
        metadata = {'account_id': self.account_id}
        tx = self._create_asset(bdb_connection, asset, metadata)
        utils.wait_until_valid(tx['id'], bdb_connection)
        tx = self._transfer_asset(bdb_connection, self.public_key, tx, metadata)
        log.info("Created document: %s - %s", self.account_id, tx['id'])
        return tx['id']


class GraphConceptAccount(BaseAccount):
    """"""

    def __init__(self, prov_element, prov_relations, namespaces, store):
        assert prov_element is not None
        assert prov_relations is not None
        assert namespaces is not None
        self.prov_element = prov_element
        self.prov_namespaces = namespaces
        self.prov_relations = prov_relations
        super().__init__(str(prov_element.identifier), store)

    def get_tx_id(self):
        return self.tx_id

    def __str__(self):
        tmp = "{} :\n".format(self.account_id)
        for k, v in self.prov_relations.items():
            tmp = tmp + str(k) + " => " + str(v) + "\n"
        return tmp

    def _create_instance_document(self):
        doc = ProvDocument()
        for n in self.prov_namespaces:
            doc.add_namespace(n.prefix, n.uri)
        doc.add_record(self.prov_element)
        return doc

    def _create_relations_document(self):
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

    def save_instance_asset(self, bdb_connection):
        if self.tx_id is None:
            prov_document = self._create_instance_document()
            asset = {'data': {'prov': prov_document.serialize(format='json')}}
            metadata = {'instance': self.account_id}
            tx = self._create_asset(bdb_connection, asset, metadata)
            utils.wait_until_valid(tx['id'], bdb_connection)
            tx = self._transfer_asset(bdb_connection, self.public_key, tx, metadata)
            self.store.set_tx_id(self.account_id, tx['id'])
            self.tx_id = tx['id']
            log.debug("Created instance: %s - %s", self.account_id, tx['id'])
        return self.tx_id

    def save_relation_assets(self, bdb_connection):
        if self.tx_id is None:
            raise Exception()
        tx_list = []
        for doc, mapping in self._create_relations_document():
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
