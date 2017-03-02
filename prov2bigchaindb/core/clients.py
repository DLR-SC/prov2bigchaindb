import logging
from prov.model import ProvDocument
from prov2bigchaindb.core import accounts, utils
from bigchaindb_driver import BigchainDB

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class BaseClient(object):
    """ BigchainDB Base Client """

    def __init__(self, host='0.0.0.0', port=9984, local_store=utils.LocalStore()):
        self.node = 'http://{}:{}'.format(host, str(port))
        self.connection = BigchainDB(self.node)
        self.store = local_store

    def _test_tx(self, tx):
        reason = None
        if not utils.is_valid_tx(tx['id'], self.connection):
            reason = "TX is invalid"
        elif not utils.is_block_to_tx_valid(tx['id'], self.connection):
            reason = "Block is invalid"
        if reason is None:
            return
        log.error("Test failed: %s", tx['id'])
        raise Exception(reason)

    def save_document(self, document):
        """
        Saves a entity, activity or entity into the database

        :param document: Document to save
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
        txid = self.account.save_asset(asset, self.connection)
        return txid

    def get_document(self, tx_id):
        log.info("Retrieve and build document")
        tx = self.connection.transactions.retrieve(tx_id)
        self._test_tx(tx)
        if 'id' in tx['asset'].keys():
            tx = self.connection.transactions.get(asset_id=tx['asset']['id'])[0]
            self._test_tx(tx)
        return ProvDocument.deserialize(content=tx['asset']['data']['prov'], format='json')


class GraphConceptClient(BaseClient):
    """"""

    def __init__(self, host='0.0.0.0', port=9984, local_store=utils.LocalStore()):
        super().__init__(host, port, local_store=local_store)
        self.accounts = []

    def save_document(self, document):
        log.info("Save document...")
        prov_document = utils.form_string(content=document)
        instance_list = utils.get_prov_element_list(prov_document)

        for prov_identifier, prov_relations, namespaces in instance_list:
            ac = accounts.GraphConceptAccount(prov_identifier, prov_relations, namespaces, self.store)
            self.accounts.append(ac)

        document_tx_ids = []
        for account in self.accounts:
            tx_id = account.save_instance_asset(self.connection)
            document_tx_ids.append(tx_id)
        for account in self.accounts:
            tx_list = account.save_relation_assets(self.connection)
            document_tx_ids += tx_list
        log.info("Saved document in %s Tx", len(document_tx_ids))
        return document_tx_ids

    def get_document(self, document_tx_ids):
        log.info("Retrieve and rebuild document...")
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
        log.info("Success")
        return doc


class RoleConceptClient(BaseClient):
    def __init__(self, host='0.0.0.0', port=9984):
        super().__init__(host, port)

    def save_document(self, document):
        """
        Saves a entity, activity or entity into the database

        :param document:
        :type document:
        :return: Record id
        :rtype: str
        """
        raise NotImplementedError("Abstract method")
