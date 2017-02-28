import logging

from prov2bigchaindb.core.utils import LocalStore

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

import unittest
from unittest import mock
from prov.model import ProvDocument
from prov2bigchaindb.tests.core import setup_test_files
from prov2bigchaindb.core import utils, clients

class DocumentConceptTest(unittest.TestCase):
    """Test BigchainDB Base Client"""

    def setUp(self):
        self.test_prov_files = setup_test_files()
        self.account_id = 'Document_Concept_Client_Test'

    def tearDown(self):
        del self.account_id
        db = LocalStore()
        db.clean_tables()
        del db
        [self.test_prov_files[k].close() for k in self.test_prov_files.keys()]

    def test_simple_prov_doc(self):
        prov_document = utils.form_string(content=self.test_prov_files["simple"])
        client = clients.DocumentConceptClient(account_id=self.account_id)
        tx_id = client.save_document(prov_document)
        ret_doc = client.get_document(tx_id)
        self.assertEqual(prov_document,ret_doc)
