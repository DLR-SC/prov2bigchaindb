from bigchaindb_driver.crypto import generate_keypair
import logging

from prov.model import ProvDocument

from prov2bigchaindb.core import utils, exceptions

log = logging.getLogger(__name__)


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
            self.public_key, self.private_key, self.tx_id = self.store.get_Account(self.account_id)
        except Exception as e:
            self.store.set_Account(self.account_id, self.public_key, self.private_key)

    def __str__(self):
        tmp = "{} : {}\n".format(self.account_id, self.public_key)
        return tmp

    def get_Id(self):
        return self.account_id

    def get_Public_Key(self):
        return self.public_key


class DocumentConceptAccount(BaseAccount):
    """"""

    def __init__(self, account_id, store):
        super().__init__(account_id, store)

    def save_Asset(self, asset, bdb_connection):

        prepared_creation_tx = bdb_connection.transactions.prepare(operation='CREATE', signers=self.public_key, asset=asset, metadata={'account_id':self.account_id})
        # print(prepared_creation_tx)
        fulfilled_creation_tx = bdb_connection.transactions.fulfill(prepared_creation_tx, private_keys=self.private_key)
        sent_creation_tx = bdb_connection.transactions.send(fulfilled_creation_tx)

        if fulfilled_creation_tx != sent_creation_tx:
            raise exceptions.CreateRecordException()
        # blocking method...
        utils.wait_until_valid(sent_creation_tx['id'], bdb_connection)
        return sent_creation_tx['id']

    def query_Asset(self, tx_id, bdb_connection):
        return bdb_connection.transactions.retrieve(tx_id)


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

    def get_TxId(self):
        return self.tx_id

    def __str__(self):
        tmp = "{} :\n".format(self.account_id)
        for k,v in self.prov_relations.items():
            tmp = tmp + str(k) + " => " + str(v) + "\n"
        return tmp

    def _create_instance_document(self):
        doc = ProvDocument()
        for n in self.prov_namespaces:
            doc.add_namespace(n.prefix, n.uri)
        doc.add_record(self.prov_element)
        return doc

    def _create_relations_document(self):
        for to, rel in self.prov_relations.items():
            doc = ProvDocument()
            for n in self.prov_namespaces:
                doc.add_namespace(n.prefix, n.uri)
            doc.add_record(rel)
            yield doc

    def save_Instance_Asset(self, bdb_connection):
        if self.tx_id is None:
            prov_document = self._create_instance_document()
            asset = {'data': {'prov': prov_document.serialize(format='json')}}
            prepared_creation_tx = bdb_connection.transactions.prepare(operation='CREATE',
                                                                       signers=self.public_key,
                                                                       asset=asset,
                                                                       metadata={'account_id':self.account_id})
            # print(prepared_creation_tx)
            fulfilled_creation_tx = bdb_connection.transactions.fulfill(prepared_creation_tx,
                                                                        private_keys=self.private_key)
            sent_creation_tx = bdb_connection.transactions.send(fulfilled_creation_tx)

            if fulfilled_creation_tx != sent_creation_tx:
                raise exceptions.CreateRecordException()
            # blocking method...
            utils.wait_until_valid(sent_creation_tx['id'], bdb_connection)
            self.store.set_Tx_Id(self.account_id, sent_creation_tx['id'])
            self.tx_id = sent_creation_tx['id']
        return self.tx_id

    def save_Relation_Assets(self, bdb_connection):
        if self.tx_id is None:
            raise Exception()
        tx_list = []
        for doc in self._create_relations_document():
            print("sender ", self.tx_id, self.public_key, self.account_id)
            for records in doc.get_records():
                recipient = self.store.get_Account(str(records.args[1]))
                asset = {'data': {'prov': doc.serialize(format='json')}}

                prepared_creation_tx = bdb_connection.transactions.prepare(operation='CREATE',
                                                                           signers=self.public_key,
                                                                           asset=asset,
                                                                           metadata={'account_id': self.account_id})
                fulfilled_creation_tx = bdb_connection.transactions.fulfill(prepared_creation_tx,
                                                                            private_keys=self.private_key)
                sent_creation_tx = bdb_connection.transactions.send(fulfilled_creation_tx)

                if fulfilled_creation_tx != sent_creation_tx:
                    raise exceptions.CreateRecordException()
                # blocking method...
                utils.wait_until_valid(sent_creation_tx['id'], bdb_connection)

                # transfer
                transfer_asset = {'id': fulfilled_creation_tx['id']}

                output_index = 0
                output = fulfilled_creation_tx['outputs'][output_index]
                transfer_input = {
                    'fulfillment': output['condition']['details'],
                    'fulfills': {
                        'output': output_index,
                        'txid': fulfilled_creation_tx['id']
                    },
                    'owners_before': output['public_keys']
                }

                prepared_transfer_tx = bdb_connection.transactions.prepare(
                    operation='TRANSFER',
                    asset=transfer_asset,
                    inputs=transfer_input,
                    recipients=recipient[0]
                )

                fulfilled_transfer_tx = bdb_connection.transactions.fulfill(
                    prepared_transfer_tx,
                    private_keys=self.private_key,
                )

                sent_transfer_tx = bdb_connection.transactions.send(fulfilled_transfer_tx)

                if fulfilled_transfer_tx != sent_transfer_tx:
                    raise exceptions.CreateRecordException()
                # blocking method...
                utils.wait_until_valid(sent_transfer_tx['id'], bdb_connection)
                try:
                    self.store.set_Document_MetaData(sent_transfer_tx['id'], recipient[0], str(records.args[1]))
                except:
                    print("\treceiver ", sent_transfer_tx['id'], recipient[0], str(records.args[1]))
                    print(sent_transfer_tx)
                    print("=======")

                tx_list.append(sent_transfer_tx['id'])
        return tx_list
#
# class RoleConceptAccount(BaseAccount):
#     """"""
#     def __init__(self, account_id, prov_relations, namespaces, account_db):
#         super().__init__(account_id, account_db)
#         self.txid = None
#         self.prov_relations = prov_relations
#         self.prov_namespaces = namespaces
