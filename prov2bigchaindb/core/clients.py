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

    def save_document(self, document):
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
        #self.store = utils.DocumentConceptMetaDataStore()

    def save_document(self, document):
        prov_document = utils.form_string(content=document)

        asset = {'data': {'prov': prov_document.serialize(format='json')}}
        txid = self.account.save_Asset(asset, self.connection)
        #self.store.set_Document_MetaData(txid, self.account.get_Public_Key(), self.account.get_Id())
        return txid

    def get_document(self, tx_id):
        tx = self.account.query_Asset(tx_id, self.connection)
        return ProvDocument.deserialize(content=tx['asset']['data']['prov'], format='json')


class GraphConceptClient(BaseClient):
    """"""

    def __init__(self, host='0.0.0.0', port=9984):
        super().__init__(host, port)
        self.accounts = None
        self.store = utils.GraphConceptMetadataStore()

    def save_document(self, document):
        prov_document = utils.form_string(content=document)
        g = prov_to_graph(prov_document)
        instance_list = utils.get_prov_element_list(prov_document)

        self.accounts = [accounts.GraphConceptAccount(prov_identifier, prov_relations, namespaces, self.accountstore)
                         for prov_identifier, prov_relations, namespaces in instance_list
        ]

        document_tx_ids = []
        for account in self.accounts:
            tx_id = account.save_Instance_Asset(self.connection)
            self.accountstore.set_Tx_Id(account.get_Id(), tx_id)
            document_tx_ids.append(tx_id)
        for account in self.accounts:
            tx_id = account.save_Relation_Assets(self.connection)
            self.store.set_Document_MetaData(tx_id, account.get_Public_Key(), account.get_Id())
        return document_tx_ids
        pass


class RoleConceptClient(BaseClient):

    def __init__(self, host='0.0.0.0', port=9984):
        super().__init__(host, port)

    def save_document(self, document):
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
