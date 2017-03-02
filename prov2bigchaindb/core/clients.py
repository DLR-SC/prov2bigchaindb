import logging
from io import BufferedReader

from prov.model import ProvDocument
from bigchaindb_driver import BigchainDB

from prov2bigchaindb.core import utils, local_stores, accounts

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class BaseClient(object):
    """ BigchainDB Base Client """

    def __init__(self, host: str = '0.0.0.0', port: int = 9984, local_store: local_stores.BaseStore = local_stores.BaseStore()):
        """
        Instantiate Base Client object

        :param host: BigchaindDB Hostname or IP (default: 0.0.0.0)
        :type host: str
        :param port: BigchaindDB Port (default: 9984)
        :type port: int
        :param local_store: Local database object
        :type local_store: BaseStore
        """
        self.node = 'http://{}:{}'.format(host, str(port))
        self.connection = BigchainDB(self.node)
        self.store = local_store

    def test_transaction(self, tx: dict) -> bool:
        """
        Test validity of transaction

        :param tx: Transaction to test
        :type tx: dict
        :return: True or Exception
        :rtype: bool
        """
        reason = None
        if not utils.is_valid_tx(tx['id'], self.connection):
            reason = "TX is invalid"
        elif not utils.is_block_to_tx_valid(tx['id'], self.connection):
            reason = "Block is invalid"
        if reason is None:
            return True
        log.error("Test failed: %s", tx['id'])
        raise Exception(reason)

    def save_document(self, document: object) -> object:
        """
        Abstract method for saving a document

        :param document: Document to save
        :type document: object
        :return: id
        :rtype: object
        """
        raise NotImplementedError("Abstract method")


class DocumentConceptClient(BaseClient):
    """"""

    def __init__(self, account_id: str = None, host: str = '0.0.0.0', port: int = 9984, local_store: local_stores.BaseStore = local_stores.BaseStore()):
        """
        Instantiate Document Client object

        :param host: BigchaindDB Hostname or IP (default: 0.0.0.0)
        :type host: str
        :param port: BigchaindDB Port (default: 9984)
        :type port: int
        :param local_store: Local database object
        :type local_store: BaseStore
        """
        super().__init__(host, port, local_store)
        self.account = accounts.DocumentConceptAccount(account_id, self.store)

    def save_document(self, document: str or BufferedReader or ProvDocument) -> str:
        """
        Writes a document into BigchainDB
        :param document: Document as JSON/XML/PROVN
        :type document: str or BufferedReader or ProvDocument
        :return: Transaction id of document
        :rtype: str
        """
        log.info("Save document...")
        prov_document = utils.form_string(content=document)
        asset = {'prov': prov_document.serialize(format='json')}
        tx_id = self.account.save_asset(asset, self.connection)
        log.info("Saved document in Tx with id: %s", tx_id)
        return tx_id

    def get_document(self, tx_id: str) -> ProvDocument:
        """
        Returns a document by transaction id from BigchainDB

        :param tx_id: Transaction Id of Document
        :type tx_id: str
        :return: Document as ProvDocument object
        :rtype: ProvDocument
        """
        log.info("Retrieve and build document")
        tx = self.connection.transactions.retrieve(tx_id)
        self.test_transaction(tx)
        if 'id' in tx['asset'].keys():
            tx = self.connection.transactions.get(asset_id=tx['asset']['id'])[0]
            self.test_transaction(tx)
        log.info("Success")
        return ProvDocument.deserialize(content=tx['asset']['data']['prov'], format='json')


class GraphConceptClient(BaseClient):
    """"""

    def __init__(self, host: str = '0.0.0.0', port: int = 9984, local_store: local_stores.BaseStore = local_stores.BaseStore()):
        """
        Instantiate Graph Client object

        :param host: BigchaindDB Hostname or IP (default: 0.0.0.0)
        :type host: str
        :param port: BigchaindDB Port (default: 9984)
        :type port: int
        :param local_store: Local database object
        :type local_store: BaseStore
        """
        super().__init__(host, port, local_store=local_store)
        self.accounts = []

    def save_document(self, document: str or BufferedReader or ProvDocument) -> list:
        """
        Writes a document into BigchainDB

        :param document: Document as JSON/XML/PROVN
        :type document: str or BufferedReader or ProvDocument
        :return: List of Transaction ids
        :rtype: list
        """
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

    def get_document(self, document_tx_ids: list) -> ProvDocument:
        """
        Returns a document by a list transaction ids from BigchainDB

        :param document_tx_ids: Transaction Ids of Document
        :type document_tx_ids: list
        :return: Document as ProvDocument object
        :rtype: ProvDocument
        """
        log.info("Retrieve and rebuild document...")
        doc = ProvDocument()
        for i in document_tx_ids:
            tx = self.connection.transactions.get(asset_id=i)[0]
            self.test_transaction(tx)
            if 'id' in tx['asset'].keys():
                tx = self.connection.transactions.get(asset_id=tx['asset']['id'])[0]
                self.test_transaction(tx)
            tmp_doc = ProvDocument.deserialize(content=tx['asset']['data']['prov'], format='json')
            for namespace in tmp_doc.get_registered_namespaces():
                doc.add_namespace(namespace)
            for record in tmp_doc.get_records():
                doc.add_record(record=record)
        log.info("Success")
        return doc


class RoleConceptClient(BaseClient):
    def __init__(self, host: str = '0.0.0.0', port: int = 9984, local_store: local_stores.BaseStore = local_stores.BaseStore()):
        """
        Instantiate Role Client object

        :param host: BigchaindDB Hostname or IP (default: 0.0.0.0)
        :type host: str
        :param port: BigchaindDB Port (default: 9984)
        :type port: int
        :param local_store: Local database object
        :type local_store: BaseStore
        """
        super().__init__(host, port, local_store=local_store)
        self.accounts = []

    def save_document(self, document: str or BufferedReader) -> list:
        """
        Writes a document into BigchainDB

        :param document: Document as JSON/XML/PROVN
        :type document: str or BufferedReader or ProvDocument
        :return: List of Transaction ids
        :rtype: list
        """
        raise NotImplementedError("")

    def get_document(self, document_tx_ids: list) -> ProvDocument:
        raise NotImplementedError("")

