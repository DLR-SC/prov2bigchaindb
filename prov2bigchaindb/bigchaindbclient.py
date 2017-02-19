from io import BufferedReader
from functools import reduce
from bigchaindb_driver.crypto import generate_keypair

from datetime import datetime
import pkg_resources

from prov2bigchaindb.adapter import BigchainDBAdapter
from prov.model import ProvDocument, six, PROV_AGENT, ProvRecord, ProvRelation, ProvActivity, ProvAgent, ProvEntity
from prov.graph import prov_to_graph, graph_to_prov

from prov2bigchaindb.exceptions.exception import NoDocumentException, ParseException

def form_string(content):
    """
    Take a string or BufferedReader as argument and transform the string into a ProvDocument
    :param content: Takes a sting or BufferedReader
    :return: ProvDocument
    """
    if isinstance(content, ProvDocument):
        return content
    elif isinstance(content, BufferedReader):
        content = reduce(lambda total, a: total + a, content.readlines())

    if type(content) is six.binary_type:
        content_str = content[0:15].decode()
        if content_str.find("{") > -1:
            return ProvDocument.deserialize(content=content, format='json')
        if content_str.find('<?xml') > -1:
            return ProvDocument.deserialize(content=content, format='xml')
        elif content_str.find('document') > -1:
            return ProvDocument.deserialize(content=content, format='provn')

    raise ParseException("Unsupported input type {}".format(type(content)))

def setup_test_files():
    test_resources = {
        'simple': {'package': 'prov2bigchaindb', 'file': '/assets/example-abstract.json'},
        'quantified': {'package': 'prov2bigchaindb', 'file': '/assets/quantified-self.json'},
        'thesis': {'package': 'prov2bigchaindb', 'file': '/assets/thesis-example-full.json'}
    }
    return dict((key, pkg_resources.resource_stream(val['package'], val['file'])) for key, val in test_resources.items())

class BigchainUser():
    def __init__(self, prov_element, prov_relations, namespaces):
        self.prov_element = prov_element
        self.bdb_txid = None
        self.prov_relations = prov_relations
        self.prov_namespaces = namespaces
        self.private_key, self.public_key = generate_keypair()

    def __str__(self):
        tmp = "{} :\n".format(self.prov_element)
        for k,v in self.prov_relations.items():
            tmp = tmp + str(k) + " => " + str(v) + "\n"
        return tmp

    def create_class(self, bdb_connection):
        doc = ProvDocument()
        for n in self.prov_namespaces:
            doc.add_namespace(n.prefix, n.uri)
        doc.add_record(self.prov_element)
        self.bdb_txid = bdb_connection.save(attributes=doc.serialize(format='json'),
                            metadata={'':''},
                            private_key=self.private_key,
                            public_key=self.public_key)
        return self.bdb_txid

    def create_relations(self, bdb_connection):
        if self.bdb_txid is None:
            raise Exception()
        for to, rel in self.prov_relations.items():
            doc = ProvDocument()
            for n in self.prov_namespaces:
                doc.add_namespace(n.prefix, n.uri)
            doc.add_record(rel)
            tx = self.bdb_txid = bdb_connection.save(attributes=doc.serialize(format='json'),
                                                       metadata={self.prov_element: self.bdb_txid},
                                                       private_key=self.private_key,
                                                       public_key=self.public_key)

            # TODO Move this into the adapter, with proper handling of public_keys
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

            prepared_transfer_tx = bdb.transactions.prepare(
                operation='TRANSFER',
                asset=transfer_asset,
                inputs=transfer_input,
                recipients=bob.public_key,
            )

            fulfilled_transfer_tx = bdb.transactions.fulfill(
                prepared_transfer_tx,
                private_keys=self.private_key,
            )
            sent_transfer_tx = bdb.transactions.send(fulfilled_transfer_tx)


def main():
    """Prov2BigchainDB Console Client"""

    # open test files
    test_prov_files =  setup_test_files()
    # read json from file into prov document
    content = test_prov_files["simple"]
    prov_document = form_string(content=content)
    # transform to graph representation
    g = prov_to_graph(prov_document)

    #print(prov_document.get_provn())

    bdb_users = []
    for node, nodes in g.adjacency_iter():
        relations = {}
        #print(node)
        for n, rel in nodes.items():
            #print("\t", n, rel)
            relations[n] = rel[0]['relation']
        bdb_u = BigchainUser(node, relations, prov_document.get_registered_namespaces())
        bdb_users.append(bdb_u)

    bdb = BigchainDBAdapter('127.0.0.1', port=59984)
    print("============")
    for u in bdb_users:
        print(u, end="\n\n")
        tx = u.create_class(bdb)
    for u in bdb_users:
        u.create_relations(bdb)

    #tx = bdb.driver.transactions.retrieve(txid=txid)
    #print(tx['asset']['data']['map'], end='\n\n')
    #p = ProvDocument.deserialize(content=tx['asset']['data']['prov'],format='json')
    #print(p.get_provn())


    # close file handles
    [test_prov_files[k].close() for k in test_prov_files.keys()]

if __name__ == "__main__":
    main()