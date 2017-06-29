import logging
from io import BufferedReader

import bigchaindb_driver as bd
import prov.graph as provgraph
import prov.model as provmodel
from bigchaindb_driver import pool as bdpool
from networkx import is_directed_acyclic_graph
from networkx import isolates
from networkx import topological_sort

from prov2bigchaindb.core import utils, local_stores, accounts

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class BaseClient(object):
    """ BigchainDB Base Client """

    def __init__(self, host: str = '0.0.0.0', port: int = 9984,
                 num_connections: int = 5, local_store: local_stores.SqliteStore = local_stores.SqliteStore()):
        """
        Instantiate Base Client object

        :param host: BigchaindDB Hostname or IP (default: 0.0.0.0)
        :type host: str
        :param port: BigchaindDB Port (default: 9984)
        :type port: int
        :param num_connections: Amount of connections made to BigchainDB node
        :type num_connections: int
        :param local_store: Local database object
        :type local_store: SqliteStore
        """
        assert num_connections > 0
        self.node = 'http://{}:{}'.format(host, str(port))
        self.connections = num_connections * [bd.BigchainDB(self.node)]
        self.connection_pool = bdpool.Pool(self.connections)
        self.store = local_store

    def test_transaction(self, tx: dict) -> bool:
        """
        Validate a transaction against BigchainDB

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
        Abstract method to store a document

        :param document: Document to save
        :type document: object
        :return: id
        :rtype: object
        """
        raise NotImplementedError("Abstract method")

    def get_document(self, document_id: object) -> provmodel.ProvDocument:
        """
        Abstract method to retrieve a document

        :param document_id: Document to save
        :type document_id: object
        :rtype: ProvDocument
        """
        raise NotImplementedError("Abstract method")


class DocumentConceptClient(BaseClient):
    """"""

    def __init__(self, account_id: str = None, host: str = '0.0.0.0', port: int = 9984, num_connections: int = 1,
                 local_store: local_stores.SqliteStore = local_stores.SqliteStore()):
        """
        Instantiate Document Client object

        :param host: BigchaindDB Hostname or IP (default: 0.0.0.0)
        :type host: str
        :param port: BigchaindDB Port (default: 9984)
        :type port: int
        :param local_store: Local database object
        :type local_store: SqliteStore
        """
        super().__init__(host, port, num_connections, local_store)
        self.account = accounts.DocumentConceptAccount(account_id, self.store)

    def save_document(self, document: str or bytes or provmodel.ProvDocument) -> str:
        """
        Write a document into BigchainDB
        
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
        Retrieve a document by transaction id from BigchainDB

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
                 local_store: local_stores.SqliteStore = local_stores.SqliteStore()):
        """
        Instantiate Graph Client object

        :param host: BigchaindDB Hostname or IP (default: 0.0.0.0)
        :type host: str
        :param port: BigchaindDB Port (default: 9984)
        :type port: int
        :param local_store: Local database object
        :type local_store: SqliteStore
        """
        super().__init__(host, port, num_connections, local_store=local_store)
        self.accounts = []

    @staticmethod
    def calculate_account_data(prov_document: provmodel.ProvDocument) -> list:
        """
        Transforms a ProvDocument into a tuple with ProvElement, list of ProvRelation and list of Namespaces

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
                for relation in tmp_relations.values():
                    relation = relation['relation']
                    if relation.identifier:
                        relations['with_id'].append(relation)
                    else:
                        relations['without_id'].append(relation)
            elements.append((node, relations, namespaces))
        return elements

    def save_document(self, document: str or BufferedReader or provmodel.ProvDocument) -> list:
        """
        Write a document into BigchainDB

        :param document: Document as JSON/XML/PROVN
        :type document: str or BufferedReader or ProvDocument
        :return: List of transaction ids
        :rtype: list
        """
        log.info("Save document...")
        document_tx_ids = []
        prov_document = utils.to_prov_document(content=document)
        elements = GraphConceptClient.calculate_account_data(prov_document)
        id_mapping = {}
        log.info("Create and Save instances")
        for prov_element, prov_relations, namespaces in elements:
            for rel in prov_relations['with_id']:
                id_mapping[rel.identifier] = ''

        for prov_element, prov_relations, namespaces in elements:
            account = accounts.GraphConceptAccount(prov_element, prov_relations, id_mapping, namespaces, self.store)
            self.accounts.append(account)
            tx_id = account.save_instance_asset(self._get_bigchain_connection())
            document_tx_ids.append(tx_id)

        log.info("Save relations with ids")
        for account in filter(lambda acc: acc.has_relations_with_id, self.accounts):
            document_tx_ids += account.save_relations_with_ids(self._get_bigchain_connection())

        log.info("Save relations without ids")
        for account in filter(lambda acc: acc.has_relations_without_id, self.accounts):
            document_tx_ids += account.save_relations_without_ids(self._get_bigchain_connection())

        log.info("Saved document in %s Tx", len(document_tx_ids))
        return document_tx_ids

    def get_document(self, document_tx_ids: list) -> provmodel.ProvDocument:
        """
        Retrieve a document by a list transaction ids from BigchainDB

        :param document_tx_ids: Transaction Ids of Document
        :type document_tx_ids: list
        :return: Document as ProvDocument object
        :rtype: ProvDocument
        """
        log.info("Retrieve and rebuild document...")
        doc = provmodel.ProvDocument()
        for i in document_tx_ids:
            log.info("tx id: %s",i)
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
                 local_store: local_stores.SqliteStore = local_stores.SqliteStore()):
        """
        Instantiate Role Client object

        :param host: BigchaindDB Hostname or IP (default: 0.0.0.0)
        :type host: str
        :param port: BigchaindDB Port (default: 9984)
        :type port: int
        :param local_store: Local database object
        :type local_store: SqliteStore
        """
        super().__init__(host, port, num_connections, local_store=local_store)
        self.accounts = []

    @staticmethod
    def calculate_account_data(prov_document: provmodel.ProvDocument) -> list:
        """
        Transforms a ProvDocument into a list of tuples including: 
        ProvAgent, list of ProvRelations from agent,
        list of ProvElements associated to ProvAgent,
        list of Namespaces

        :param prov_document: Document to transform
        :type prov_document:
        :return: List of tuples(ProvAgent, list(), list(), list())
        :rtype: list
        """

        namespaces = prov_document.get_registered_namespaces()
        g = provgraph.prov_to_graph(prov_document=prov_document)
        sorted_nodes = topological_sort(g, reverse=True)
        agents = list(filter(lambda elem: isinstance(elem, provmodel.ProvAgent), sorted_nodes))
        elements = list(filter(lambda elem: not isinstance(elem, provmodel.ProvAgent), sorted_nodes))

        # Check on compatibility
        if not is_directed_acyclic_graph(g):
            raise Exception("Provenance graph is not acyclic")
        if isolates(g):
            raise Exception("Provenance not compatible with role-based concept. Has isolated Elements")
        for element in elements:
            if provmodel.ProvAgent not in [type(n) for n in g.neighbors(element)]:
                raise Exception(
                    "Provenance not compatible with role-based concept. Element {} has not relation to any agent".format(
                        element))

        accounts = []
        for agent in agents:
            # find out-going relations from agent
            agent_relations = []
            for u, v in g.out_edges(agent):
                # Todo check if filter does not left out some info
                agent_relations.append(g.get_edge_data(u, v)[0]['relation'])

            agent_elements = {}
            i = 0
            for element in elements:
                element_relations = []
                if g.has_edge(element, agent):
                    for u, v in set(g.out_edges(element)):
                        for relation in g[u][v].values():
                            element_relations.append(relation['relation'])
                    agent_elements[i] = {element: element_relations}
                    i += 1

            accounts.append((agent, agent_relations, agent_elements, namespaces))
        return accounts

    def save_document(self, document: str or BufferedReader or provmodel.ProvDocument) -> list:
        """
        Write a document into BigchainDB

        :param document: Document as JSON/XML/PROVN
        :type document: str or BufferedReader or ProvDocument
        :return: List of transaction ids
        :rtype: list
        """
        log.info("Save document...")
        document_tx_ids = []
        prov_document = utils.to_prov_document(content=document)
        account_data = RoleConceptClient.calculate_account_data(prov_document)

        id_mapping = {}
        log.info("Create and Save instances")
        for agent, relations, elements, namespaces in account_data:
            account = accounts.RoleConceptAccount(agent, relations, elements, id_mapping, namespaces, self.store)
            self.accounts.append(account)
            tx_id = account.save_instance_asset(self._get_bigchain_connection())
            document_tx_ids.append(tx_id)

        log.info("Save elements")
        for account in self.accounts:
            document_tx_ids += account.save_elements(self._get_bigchain_connection())

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















