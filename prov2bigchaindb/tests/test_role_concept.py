import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

import unittest

class RoleConceptTest(unittest.TestCase):
    """Test BigchainDB Base Client"""

    def setUp(self):
        self.db_name = 'test_role_concept.db'
        self.account_id = 'Role_Concept_Client_Test'
        self.public_key = 'public'
        self.private_key = 'private'
        self.host = '127.0.0.1'
        self.port = 9984

    def tearDown(self):
        #db = LocalStore()
        #db.clean_tables()
        #del db
        pass

    @unittest.skip("testing skipping")
    def test_simple_prov_doc(self):
        pass

