from prov.graph import prov_to_graph
from prov.model import ProvDocument
from prov2bigchaindb.core import accounts, utils
from bigchaindb_driver import BigchainDB
import logging


log = logging.getLogger(__name__)


class BaseClient(object):
    """ BigchainDB Base Client """

    def __init__(self, host='0.0.0.0', port=9984):
        self.node = 'http://{}:{}'.format(host, str(port))
        self.connection = BigchainDB(self.node)
        self.accountstore = utils.LocalAccountStore()

    def save(self, document):
        """
        Saves a entity, activity or entity into the database

        :param document: Document to save
        :type attributes: str
        :return: document id
        :rtype: str
        """
        raise NotImplementedError("Abstract method")


class DocumentConceptClient(BaseClient):
    """"""

    def __init__(self, account_id=None, host='0.0.0.0', port=9984):
        super().__init__(host, port)
        self.account = accounts.DocumentConceptAccount(account_id, self.accountstore)
        #self.documentstore = utils.DocumentModelMetaDataStore()

    def save(self, document):
        prov_document = utils.form_string(content=document)

        asset = {'data': {'prov': prov_document.serialize(format='json')}}
        txid = self.account.save_Asset(asset, self.connection)
        #self.documentstore.set_Document_MetaData(txid, self.account.get_Public_Key(), self.account.get_Id())
        return txid

    def get_document(self, tx_id):
        tx = self.account.query_Asset(tx_id, self.connection)
        return ProvDocument.deserialize(content=tx['asset']['data']['prov'], format='json')


class GraphConceptClient(BaseClient):
    """"""

    def __init__(self, host='0.0.0.0', port=9984):
        super().__init__(host, port)

    def save(self, document):
        # prov_document = utils.form_string(content=document)
        # g = prov_to_graph(prov_document)
        #
        # bdb_users = []
        # for node, nodes in g.adjacency_iter():
        #     relations = {}
        #     # print(node)
        #     for n, rel in nodes.items():
        #         # print("\t", n, rel)
        #         relations[n] = rel[0]['relation']
        #     bdb_u = DocumentModelAccount(node, relations, prov_document.get_registered_namespaces())
        #     bdb_users.append(bdb_u)
        #
        # bdb = DocumentModelClient('127.0.0.1', port=59984)
        # print("============")
        # for u in bdb_users:
        #     print(u, end="\n\n")
        #     self.bdb_txid = self.driver.transactions.prepare(operation='CREATE', signers=, asset=asset,
        #                                                         metadata=metadata)
        #
        #     tx = u.create_class(bdb)
        # for u in bdb_users:
        #     u.create_relations(bdb)
        #
        # asset = {'data': {'prov': attributes, 'map': metadata}}
        # prepared_creation_tx = self.driver.
        # # print(prepared_creation_tx)
        # fulfilled_creation_tx = self.driver.transactions.fulfill(prepared_creation_tx, private_keys=private_key)
        # sent_creation_tx = self.driver.transactions.send(fulfilled_creation_tx)
        #
        # if fulfilled_creation_tx != sent_creation_tx:
        #     raise CreateRecordException()
        # trials = 0
        # while trials < 100:
        #     try:
        #         if self.driver.transactions.status(sent_creation_tx['id']).get('status') == 'valid':
        #             break
        #     except NotFoundError:
        #         trials += 1
        # return sent_creation_tx['id']
        pass


class RoleConceptClient(BaseClient):

    def __init__(self, host='0.0.0.0', port=9984):
        super().__init__(host, port)

    def save(self, document):
        """
        Saves a entity, activity or entity into the database

        :param attributes: Attributes as dict for the record. Be careful you have to encode the dict
        :type attributes: dict
        :param metadata: Metadata as dict for the record. Be careful you have to encode the dict but you can be sure that all meta keys are always there
        :type metadata: dict
        :return: Record id
        :rtype: str
        """
        raise NotImplementedError("Abstract method")
