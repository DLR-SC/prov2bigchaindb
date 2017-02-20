from bigchaindb_driver.crypto import generate_keypair
import logging
from prov2bigchaindb.core import utils, exceptions

log = logging.getLogger(__name__)


class BaseAccount(object):
    """ BigchainDB Base Account """

    def __init__(self, account_id, account_db):
        assert isinstance(account_id,str)
        assert isinstance(account_db,utils.LocalAccountStore)
        self.account_db = account_db
        self.account_id = account_id
        self.private_key, self.public_key = generate_keypair()
        try:
            self.public_key, self.private_key, self.txid = self.account_db.get_Account(self.account_id)
        except Exception:
            self.account_db.set_Account(self.account_id, self.public_key, self.private_key)

    def __str__(self):
        tmp = "{} : {}\n".format(self.account_id, self.public_key)
        return tmp

    def get_Id(self):
        return self.account_id

    def get_Public_Key(self):
        return self.public_key


class DocumentModelAccount(BaseAccount):
    """"""

    def __init__(self, account_id, account_db):
        super().__init__(account_id, account_db)

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

    def get_Asset(self, tx_id, bdb_connection):
        return bdb_connection.transactions.retrieve(tx_id)


# class GraphModelAccount(BaseAccount):
#     """"""
#
#     def __init__(self, account_id, prov_relations, namespaces, account_db):
#         super().__init__(account_id, account_db)
#         self.txid = None
#         self.prov_namespaces = namespaces
#         self.prov_relations = prov_relations
#
#     def get_TxId(self):
#         return self.txid
#
#
# class RoleModelAccount(BaseAccount):
#     """"""
#     def __init__(self, account_id, prov_relations, namespaces, account_db):
#         super().__init__(account_id, account_db)
#         self.txid = None
#         self.prov_relations = prov_relations
#         self.prov_namespaces = namespaces
#
#     def __str__(self):
#         tmp = "{} :\n".format(self.account_id)
#         for k,v in self.prov_relations.items():
#             tmp = tmp + str(k) + " => " + str(v) + "\n"
#         return tmp
#
#     def get_TxId(self):
#         return self.txid
#
#     def _create_class(self):
#         doc = ProvDocument()
#         for n in self.prov_namespaces:
#             doc.add_namespace(n.prefix, n.uri)
#         doc.add_record(self.account_id)
#         return doc
#
#     def _create_relations(self):
#         doc = ProvDocument()
#         for to, rel in self.prov_relations.items():
#             for n in self.prov_namespaces:
#                 doc.add_namespace(n.prefix, n.uri)
#             doc.add_record(rel)
#         return doc
#
#     def get_class(self):
#         return self._create_class()
#
#     def get_relations(self):
#         if self.txid is None:
#             raise Exception()
#         return self._create_relations()