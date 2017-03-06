import logging
from io import BufferedReader

import prov.model as provmodel
import prov.graph as provgraph
import bigchaindb_driver as bd
from bigchaindb_driver import pool as bdpool
from prov2bigchaindb.core import utils, local_stores, accounts

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class BaseClient(object):
    """ BigchainDB Base Client """

    def __init__(self, host: str = '0.0.0.0', port: int = 9984, num_connections: int = 5, local_store: local_stores.BaseStore = local_stores.BaseStore()):
        """
        Instantiate Base Client object

        :param num_connections: Amount of bigchaindb connection to setup (default: 5)
        :type int
        :param host: BigchaindDB Hostname or IP (default: 0.0.0.0)
        :type host: str
        :param port: BigchaindDB Port (default: 9984)
        :type port: int
        :param local_store: Local database object
        :type local_store: BaseStore
        """
        assert num_connections > 0
        self.node = 'http://{}:{}'.format(host, str(port))
        self.connections = num_connections * [bd.BigchainDB(self.node)]
        self.connection_pool = bdpool.Pool(self.connections)
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
        if not utils.is_valid_tx(tx['id'], self.connection_pool.get_connection()):
            reason = "TX is invalid"
        elif not utils.is_block_to_tx_valid(tx['id'], self.connection_pool.get_connection()):
            reason = "Block is invalid"
        if reason is None:
            return True
        log.error("Test failed: %s", tx['id'])
        raise Exception(reason)

    def _get_bigchain_connection(self) -> bd.BigchainDB:
        """
        Returns BigchainDB connection
        :return: BigchainDB connection object
        :rtype: bd.BigchainDB
        """
        return self.connection_pool.get_connection()

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

    def __init__(self, account_id: str = None, host: str = '0.0.0.0', port: int = 9984, num_connections: int = 1,
                 local_store: local_stores.BaseStore = local_stores.BaseStore()):
        """
        Instantiate Document Client object

        :param host: BigchaindDB Hostname or IP (default: 0.0.0.0)
        :type host: str
        :param port: BigchaindDB Port (default: 9984)
        :type port: int
        :param local_store: Local database object
        :type local_store: BaseStore
        """
        super().__init__(host, port, num_connections, local_store)
        self.account = accounts.DocumentConceptAccount(account_id, self.store)

    def save_document(self, document: str or bytes or provmodel.ProvDocument) -> str:
        """
        Writes a document into BigchainDB
        :param document: Document as JSON/XML/PROVN
        :type document: str or bytes or ProvDocument
        :return: Transaction id of document
        :rtype: str
        """
        log.info("Save document...")
        prov_document = utils.to_prov_document(content=document)
        asset = {'prov': prov_document.serialize(format='json')}
        tx_id = self.account.save_asset(asset, self._get_bigchain_connection())
        log.info("Saved document in Tx with id: %s", tx_id)
        return tx_id

    def get_document(self, tx_id: str) -> provmodel.ProvDocument:
        """
        Returns a document by transaction id from BigchainDB

        :param tx_id: Transaction Id of Document
        :type tx_id: str
        :return: Document as ProvDocument object
        :rtype: ProvDocument
        """
        log.info("Retrieve and build document")
        tx = self._get_bigchain_connection().transactions.retrieve(tx_id)
        self.test_transaction(tx)
        if 'id' in tx['asset'].keys():
            tx = self._get_bigchain_connection().transactions.get(asset_id=tx['asset']['id'])[0]
            self.test_transaction(tx)
        log.info("Success")
        return utils.to_prov_document(tx['asset']['data']['prov'])


class GraphConceptClient(BaseClient):
    """"""

    def __init__(self, host: str = '0.0.0.0', port: int = 9984, num_connections: int = 5,
                 local_store: local_stores.BaseStore = local_stores.BaseStore()):
        """
        Instantiate Graph Client object

        :param host: BigchaindDB Hostname or IP (default: 0.0.0.0)
        :type host: str
        :param port: BigchaindDB Port (default: 9984)
        :type port: int
        :param local_store: Local database object
        :type local_store: BaseStore
        """
        super().__init__(host, port, num_connections, local_store=local_store)
        self.accounts = []

    @staticmethod
    def get_prov_element_list(prov_document: provmodel.ProvDocument) -> list:
        """
        Transforms a ProvDocument into a tuple including ProvElement, list of ProvRelation and list of Namespaces

        :param prov_document: Document to transform
        :type prov_document:
        :return: List of tuples(element, relations, namespace)
        :rtype: list
        """

        namespaces = prov_document.get_registered_namespaces()
        g = provgraph.prov_to_graph(prov_document=prov_document)
        elements = []
        for node, nodes in g.adjacency_iter():
            relations = {'with_id': [], 'without_id': []}
            # print(node)
            for tmp_relations in nodes.values():
                # print("\t",tmp_relations)
                for relation in tmp_relations.values():
                    relation = relation['relation']
                    # print("\t\t", relation)
                    # print("\t\t\t", relation.identifier)
                    # print("\t\t\t", type(relation.identifier))
                    if relation.identifier:
                        relations['with_id'].append(relation)
                    else:
                        relations['without_id'].append(relation)
            elements.append((node, relations, namespaces))
        return elements

    def save_document(self, document: str or BufferedReader or provmodel.ProvDocument) -> list:
        """
        Writes a document into BigchainDB

        :param document: Document as JSON/XML/PROVN
        :type document: str or BufferedReader or ProvDocument
        :return: List of transaction ids
        :rtype: list
        """
        log.info("Save document...")
        document_tx_ids = []
        prov_document = utils.to_prov_document(content=document)
        elements = GraphConceptClient.get_prov_element_list(prov_document)
        id_mapping = {}
        log.info("Create and Save instances")
        for prov_element, prov_relations, namespaces in elements:
            for rel in prov_relations['with_id']:
                id_mapping[rel.identifier] = ''
            account = accounts.GraphConceptAccount(prov_element, prov_relations, id_mapping, namespaces, self.store)
            self.accounts.append(account)
            tx_id = account.save_instance_asset(self._get_bigchain_connection())
            document_tx_ids.append(tx_id)

        log.info("Save relations with ids")
        for account in filter(lambda acc: acc.has_relations_without_id, self.accounts):
            document_tx_ids += account.save_relations_with_ids(self._get_bigchain_connection())

        log.info("Save relations without ids")
        for account in filter(lambda acc: acc.has_relations_without_id, self.accounts):
            document_tx_ids += account.save_relations_without_ids(self._get_bigchain_connection())

        log.info("Saved document in %s Tx", len(document_tx_ids))
        return document_tx_ids

    def get_document(self, document_tx_ids: list) -> provmodel.ProvDocument:
        """
        Returns a document by a list transaction ids from BigchainDB

        :param document_tx_ids: Transaction Ids of Document
        :type document_tx_ids: list
        :return: Document as ProvDocument object
        :rtype: ProvDocument
        """
        log.info("Retrieve and rebuild document...")
        doc = provmodel.ProvDocument()
        for i in document_tx_ids:
            tx = self._get_bigchain_connection().transactions.get(asset_id=i)[0]
            self.test_transaction(tx)
            if 'id' in tx['asset'].keys():
                tx = self._get_bigchain_connection().transactions.get(asset_id=tx['asset']['id'])[0]
                self.test_transaction(tx)
            tmp_doc = utils.to_prov_document(tx['asset']['data']['prov'])
            for namespace in tmp_doc.get_registered_namespaces():
                doc.add_namespace(namespace)
            for record in tmp_doc.get_records():
                doc.add_record(record=record)
        log.info("Success")
        return doc


class RoleConceptClient(BaseClient):
    """"""

    def __init__(self, host: str = '0.0.0.0', port: int = 9984, num_connections: int = 5,
                 local_store: local_stores.BaseStore = local_stores.BaseStore()):
        """
        Instantiate Role Client object

        :param host: BigchaindDB Hostname or IP (default: 0.0.0.0)
        :type host: str
        :param port: BigchaindDB Port (default: 9984)
        :type port: int
        :param local_store: Local database object
        :type local_store: BaseStore
        """
        super().__init__(host, port, num_connections, local_store=local_store)
        self.accounts = []

    @staticmethod
    def get_prov_element_list(prov_document: provmodel.ProvDocument) -> list:
        """
        Transforms a ProvDocument into a tuple including ProvElement, list of ProvRelation and list of Namespaces

        :param prov_document: Document to transform
        :type prov_document:
        :return: List of tuples(element, relations, namespace)
        :rtype: list
        """

        namespaces = prov_document.get_registered_namespaces()
        g = provgraph.prov_to_graph(prov_document=prov_document)
        elements = []
        for node, nodes in g.adjacency_iter():
            relations = {'with_id': [], 'without_id': []}
            # print(node)
            for tmp_relations in nodes.values():
                # print("\t",tmp_relations)
                for relation in tmp_relations.values():
                    relation = relation['relation']
                    # print("\t\t", relation)
                    # print("\t\t\t", relation.identifier)
                    # print("\t\t\t", type(relation.identifier))
                    if relation.identifier:
                        relations['with_id'].append(relation)
                    else:
                        relations['without_id'].append(relation)
            elements.append((node, relations, namespaces))
        return elements

    def save_document(self, document: str or BufferedReader or provmodel.ProvDocument) -> list:
        """
        Writes a document into BigchainDB

        :param document: Document as JSON/XML/PROVN
        :type document: str or BufferedReader or ProvDocument
        :return: List of transaction ids
        :rtype: list
        """
        log.info("Save document...")
        document_tx_ids = []
        prov_document = utils.to_prov_document(content=document)
        elements = RoleConceptClient.get_prov_element_list(prov_document)
        id_mapping = {}
        log.info("Create and Save instances")
        for prov_element, prov_relations, namespaces in elements:
            for rel in prov_relations['with_id']:
                id_mapping[rel.identifier] = ''
            account = accounts.RoleConceptAccount(prov_element, prov_relations, id_mapping, namespaces, self.store)
            self.accounts.append(account)
            tx_id = account.save_instance_asset(self._get_bigchain_connection())
            document_tx_ids.append(tx_id)

        log.info("Save relations with ids")
        for account in filter(lambda acc: acc.has_relations_without_id, self.accounts):
            document_tx_ids += account.save_relations_with_ids(self._get_bigchain_connection())

        log.info("Save relations without ids")
        for account in filter(lambda acc: acc.has_relations_without_id, self.accounts):
            document_tx_ids += account.save_relations_without_ids(self._get_bigchain_connection())

        log.info("Saved document in %s Tx", len(document_tx_ids))
        return document_tx_ids

    def get_document(self, document_tx_ids: list) -> provmodel.ProvDocument:
        """
        Returns a document by a list transaction ids from BigchainDB

        :param document_tx_ids: Transaction Ids of Document
        :type document_tx_ids: list
        :return: Document as ProvDocument object
        :rtype: ProvDocument
        """
        log.info("Retrieve and rebuild document...")
        doc = provmodel.ProvDocument()
        for i in document_tx_ids:
            tx = self._get_bigchain_connection().transactions.get(asset_id=i)[0]
            self.test_transaction(tx)
            if 'id' in tx['asset'].keys():
                tx = self._get_bigchain_connection().transactions.get(asset_id=tx['asset']['id'])[0]
                self.test_transaction(tx)
            tmp_doc = utils.to_prov_document(tx['asset']['data']['prov'])
            for namespace in tmp_doc.get_registered_namespaces():
                doc.add_namespace(namespace)
            for record in tmp_doc.get_records():
                doc.add_record(record=record)
        log.info("Success")
        return doc
