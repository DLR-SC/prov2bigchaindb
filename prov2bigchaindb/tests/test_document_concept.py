import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from prov2bigchaindb.core.utils import LocalStore
import unittest
from prov2bigchaindb.tests.core import setup_test_files
from prov2bigchaindb.core import utils, clients
from time import sleep

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

    @unittest.skip("testing skipping")
    def test_simple_prov_doc(self):
        prov_document = utils.form_string(content=self.test_prov_files["simple"])
        client = clients.DocumentConceptClient(account_id=self.account_id)
        tx_id = client.save_document(prov_document)
        sleep(1)
        ret_doc = client.get_document(tx_id)
        self.assertEqual(prov_document,ret_doc)
