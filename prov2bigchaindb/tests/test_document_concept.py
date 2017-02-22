import unittest
from unittest import mock
from prov.model import ProvDocument
from prov2bigchaindb.tests.core import setup_test_files
from prov2bigchaindb.core import utils, clients

class DocumentConceptTest(unittest.TestCase):
    """Test BigchainDB Base Client"""

    def setUp(self):
        self.test_prov_files = setup_test_files()
        self.account_id = 'Base_Client_Test'

    def tearDown(self):
        import os
        os.remove('config.db')

    def test_simple_prov_doc(self):
        prov_document = utils.form_string(content=self.test_prov_files["simple"])
        client = clients.DocumentConceptClient(account_id=self.account_id)
        tx_id = client.save(prov_document)
        ret_doc = client.get_document(tx_id)
        self.assertEqual(prov_document,ret_doc)