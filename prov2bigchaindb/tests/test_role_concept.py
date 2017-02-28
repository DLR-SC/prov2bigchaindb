import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

import unittest
from unittest import mock
from prov2bigchaindb.tests.core import setup_test_files

from prov2bigchaindb.core import utils, clients
from prov.model import ProvDocument

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
        import os
        os.remove(self.db_name)

    @unittest.skip("testing skipping")
    def test_simple_prov_doc(self):
        pass

