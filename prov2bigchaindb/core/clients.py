import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


from prov.graph import prov_to_graph
from prov.model import ProvDocument
from prov2bigchaindb.core import accounts, utils
from bigchaindb_driver import BigchainDB



class BaseClient(object):
    """ BigchainDB Base Client """

    def __init__(self, host='0.0.0.0', port=9984, local_store=utils.LocalStore()):
        self.node = 'http://{}:{}'.format(host, str(port))
        self.connection = BigchainDB(self.node)
        self.store = local_store

    def _test_tx(self, tx):
        reason = "Yet not checked"

        if not utils.is_valid_tx(tx['id'], self.connection):
            reason = "TX is invalid"
        elif not utils.is_block_to_tx_valid(tx['id'], self.connection):
            reason = "Block is invalid"
        else:
            return
        raise Exception(reason)

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
        self.account = accounts.DocumentConceptAccount(account_id, self.store)

    def save_document(self, document):
        prov_document = utils.form_string(content=document)
        asset = {'prov': prov_document.serialize(format='json')}
        txid = self.account.save_Asset(asset, self.connection)
        #self.store.set_Document_MetaData(txid, self.account.get_Public_Key(), self.account.get_Id())
        return txid

    def get_document(self, tx_id):
        tx = self.connection.transactions.retrieve(tx_id)
        self._test_tx(tx)
        return ProvDocument.deserialize(content=tx['asset']['data']['prov'], format='json')


class GraphConceptClient(BaseClient):
    """"""

    def __init__(self, host='0.0.0.0', port=9984, local_store=utils.GraphConceptMetadataStore()):
        super().__init__(host, port, local_store=local_store)
        self.accounts = []


    def save_document(self, document):
        prov_document = utils.form_string(content=document)
        g = prov_to_graph(prov_document)
        instance_list = utils.get_prov_element_list(prov_document)

        for prov_identifier, prov_relations, namespaces in instance_list:
            ac = accounts.GraphConceptAccount(prov_identifier, prov_relations, namespaces, self.store)
            self.accounts.append(ac)

        document_tx_ids = []
        for account in self.accounts:
            tx_id = account.save_Instance_Asset(self.connection)
            document_tx_ids.append(tx_id)
        for account in self.accounts:
            tx_list = account.save_Relation_Assets(self.connection)
            for tx_id in tx_list:
                document_tx_ids.append(tx_id)
        return document_tx_ids

    def get_document(self, document_tx_ids):
        doc = ProvDocument()
        for i in document_tx_ids:
            tx = self.connection.transactions.get(asset_id=i)[0]
            self._test_tx(tx)
            if 'id' in tx['asset'].keys():
                tx = self.connection.transactions.get(asset_id=tx['asset']['id'])[0]
                self._test_tx(tx)
            tmp_doc = ProvDocument.deserialize(content=tx['asset']['data']['prov'], format='json')
            for namespace in tmp_doc.get_registered_namespaces():
                doc.add_namespace(namespace)
            for record in tmp_doc.get_records():
                doc.add_record(record=record)
        return doc

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
