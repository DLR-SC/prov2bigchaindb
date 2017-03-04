import logging
import unittest
from unittest import mock
from . import setup_test_files
import bigchaindb_driver
from prov2bigchaindb.core import accounts, utils, exceptions, local_stores

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class BaseAccountTest(unittest.TestCase):
    def setUp(self):
        self.account_id = 'Base_Account_Test'
        self.public_key = 'public'
        self.private_key = 'private'

        self.store = mock.Mock(spec=local_stores.BaseStore,
                               **{'get_account.return_value': (self.account_id,
                                                                             self.public_key,
                                                                             self.private_key,
                                                                             None)}
                               )

    def tearDown(self):
        del self.account_id
        del self.public_key
        del self.private_key
        del self.store

    def test_positive_init(self):
        account = accounts.BaseAccount(self.account_id, self.store)
        self.assertIsInstance(account, accounts.BaseAccount)
        self.assertIsInstance(account.public_key, str)
        self.assertIsInstance(account.private_key, str)
        self.assertEqual(account.get_public_key(), self.public_key)

    def test_positive_init_without_Account(self):
        self.store.configure_mock(**{'get_account.side_effect': exceptions.NoAccountException()})
        account = accounts.BaseAccount(self.account_id, self.store)
        self.assertNotEqual(account.get_public_key(), self.public_key)

    def test_negative_init_BaseAccount(self):
        with self.assertRaises(AssertionError):
            accounts.BaseAccount(self.account_id, None)

    def test__str__(self):
        account = accounts.BaseAccount(self.account_id, self.store)
        self.assertEqual(str(account), self.account_id +" : " +  self.public_key)

    def test_positive_get_id(self):
        account = accounts.BaseAccount(self.account_id, self.store)
        self.assertIsInstance(account.get_id(), str)
        self.assertEqual(account.get_id(), self.account_id)

    def test_positive_get_public_Key(self):
        account = accounts.BaseAccount(self.account_id, self.store)
        self.assertIsInstance(account.get_public_key(), str)
        self.assertEqual(account.get_public_key(), self.public_key)

    @unittest.skip("testing skipping")
    def test__create_asset(self):
        raise NotImplementedError()

    @unittest.skip("testing skipping")
    def test__transfer_asset(self):
        raise NotImplementedError()


class DocumentConceptAccountTest(unittest.TestCase):
    def setUp(self):
        self.account_id = 'Document_Concept_Account_Test'
        self.public_key = 'public'
        self.private_key = 'private'
        self.store = mock.Mock(spec=local_stores.BaseStore,
                               **{'get_account.return_value': (
                                        self.account_id,
                                        self.public_key,
                                        self.private_key,
                                        None)})

        self.return_value = {"operation": "CREATE",
                             "outputs": [{"amount": 1,
                                          "condition": {
                                              "details": {
                                                  "bitmask": 32,
                                                  "public_key": "4K9sWUMFwTgaDGPfdynrbxWqWS6sWmKbZoTjxLtVUibD",
                                                  "signature": None,
                                                  "type": "fulfillment",
                                                  "type_id": 4
                                              },
                                              "uri": "cc:4:20:MTmLrdyfhfxPw3WxnaYaQkPmU1GcEzg9mAj_O_Nuv5w:96"
                                          },
                                          "public_keys": [
                                              "4K9sWUMFwTgaDGPfdynrbxWqWS6sWmKbZoTjxLtVUibD"
                                          ]
                                          }
                                         ],
                             'id': '1',
                             'asset': {'data': {'prov': '1'}}}

        self.bdb_connection = mock.Mock(spec=bigchaindb_driver.BigchainDB,
                                        **{'transactions.retrieve.return_value': self.return_value,
                                           'transactions.prepare.return_value': self.return_value,
                                           'transactions.fulfill.return_value': self.return_value,
                                           'transactions.send.return_value': self.return_value,
                                           }
                                        )

    def tearDown(self):
        del self.account_id
        del self.public_key
        del self.private_key
        del self.store
        del self.bdb_connection

    @mock.patch('prov2bigchaindb.core.utils.wait_until_valid')
    def test_positive_save_asset(self, mock_wait):
        asset = {'data': {'prov': ''}}
        account = accounts.DocumentConceptAccount(self.account_id, self.store)
        tx_id = account.save_asset(asset, self.bdb_connection)
        # self.bdb_connection.transactions.prepare.assert_called_with(operation='CREATE', signers=self.public_key, asset={'data':asset}, metadata={'account_id':self.account_id})
        self.bdb_connection.transactions.fulfill.assert_called_with(self.return_value, private_keys=self.private_key)
        self.bdb_connection.transactions.send.assert_called_with(self.return_value)
        self.assertEqual(tx_id, '1')

    @mock.patch('prov2bigchaindb.core.utils.wait_until_valid')
    def test_negative_save_asset(self, mock_wait):
        asset = {'data': {'prov': ''}}
        account = accounts.DocumentConceptAccount(self.account_id, self.store)
        negative_return = self.return_value['id'] = '2'
        self.bdb_connection.configure_mock(**{'transactions.retrieve.return_value': self.return_value,
                                              'transactions.prepare.return_value': self.return_value,
                                              'transactions.fulfill.return_value': self.return_value,
                                              'transactions.send.return_value': negative_return,
                                              })
        with self.assertRaises(exceptions.CreateRecordException):
            account.save_asset(asset, self.bdb_connection)
        # self.bdb_connection.transactions.prepare.assert_called_with(operation='CREATE', signers=self.public_key, asset={'data':asset}, metadata={'account_id':self.account_id})
        self.bdb_connection.transactions.fulfill.assert_called_with(self.return_value, private_keys=self.private_key)
        self.bdb_connection.transactions.send.assert_called_with(self.return_value)


class GraphConceptAccountTest(unittest.TestCase):
    def setUp(self):
        self.test_prov_files = setup_test_files()
        self.prov_document = utils.to_prov_document(content=self.test_prov_files["simple"])
        self.prov_element, self.prov_relations, self.prov_namespaces = utils.get_prov_element_list(self.prov_document)['independent'][0]
        self.public_key = 'public'
        self.private_key = 'private'
        self.store = mock.Mock(spec=local_stores.BaseStore,
                               **{'get_account.return_value': (
                                   str(self.prov_element.identifier),
                                   self.public_key,
                                   self.private_key,
                                   None)})

        self.return_value = {"operation": "CREATE",
                             "outputs": [{"amount": 1,
                                          "condition": {
                                              "details": {
                                                  "bitmask": 32,
                                                  "public_key": "4K9sWUMFwTgaDGPfdynrbxWqWS6sWmKbZoTjxLtVUibD",
                                                  "signature": None,
                                                  "type": "fulfillment",
                                                  "type_id": 4
                                              },
                                              "uri": "cc:4:20:MTmLrdyfhfxPw3WxnaYaQkPmU1GcEzg9mAj_O_Nuv5w:96"
                                          },
                                          "public_keys": [
                                              "4K9sWUMFwTgaDGPfdynrbxWqWS6sWmKbZoTjxLtVUibD"
                                          ]
                                          }
                                         ],
                             'id': '1',
                             'asset': {'data': {'prov': '1'}}
                             }
        self.bdb_connection = mock.Mock(spec=bigchaindb_driver.BigchainDB,
                                        **{'transactions.retrieve.return_value': self.return_value,
                                           'transactions.prepare.return_value': self.return_value,
                                           'transactions.fulfill.return_value': self.return_value,
                                           'transactions.send.return_value': self.return_value})

    def tearDown(self):
        del self.prov_document
        del self.prov_element
        del self.prov_relations
        del self.prov_namespaces
        del self.public_key
        del self.private_key
        del self.store
        del self.bdb_connection
        del self.test_prov_files

    def test_positive_init_without_account(self):
        self.store.configure_mock(**{'get_account.side_effect': exceptions.NoAccountException()})
        account = accounts.GraphConceptAccount(self.prov_element, self.prov_relations, self.prov_namespaces, self.store)
        self.assertNotEqual(account.get_public_key(), self.public_key)
        self.assertEqual(account.tx_id, '')
        self.assertEqual(account.prov_namespaces, self.prov_namespaces)
        self.assertEqual(account.prov_independent_relations, self.prov_relations['independent'])
        self.assertEqual(account.prov_dependent_relations, self.prov_relations['dependent'])


    def test__str__(self):
        account = accounts.GraphConceptAccount(self.prov_element, self.prov_relations, self.prov_namespaces, self.store)
        self.assertEqual(str(account), str(self.prov_element.identifier) + " : " + self.public_key +
                         "\n\t" + str(self.prov_relations['independent']) +
                         "\n\t" + str(self.prov_relations['dependent'])
                         )

    def test_get_tx_id(self):
        account = accounts.GraphConceptAccount(self.prov_element, self.prov_relations, self.prov_namespaces, self.store)
        account.tx_id = '1'
        self.assertEqual(account.get_tx_id(), '1')

    @mock.patch('prov2bigchaindb.core.utils.wait_until_valid')
    def test_positiv_save_instance_asset(self, mock_wait):
        self.store.configure_mock(**{'get_account.side_effect': exceptions.NoAccountException()})
        account = accounts.GraphConceptAccount(self.prov_element, self.prov_relations, self.prov_namespaces, self.store)
        tx_id = account.save_instance_asset(self.bdb_connection)
        # asset = {'data': {'prov': account._create_instance_document().serialize(format='json')}}
        # self.bdb_connection.transactions.prepare.assert_called_with(operation='CREATE', signers=account.public_key, asset=asset, metadata={'account_id':str(self.prov_element.identifier)})
        self.bdb_connection.transactions.fulfill.assert_called_with(self.return_value, private_keys=account.private_key)
        self.bdb_connection.transactions.send.assert_called_with(self.return_value)
        self.assertEqual(tx_id, '1')
        self.assertEqual(account.get_tx_id(), '1')

    @mock.patch('prov2bigchaindb.core.utils.wait_until_valid')
    def test_negativ_save_instance_asset(self, mock_wait):
        self.store.configure_mock(**{'get_account.side_effect': exceptions.NoAccountException()})
        account = accounts.GraphConceptAccount(self.prov_element, self.prov_relations, self.prov_namespaces, self.store)
        negative_return = self.return_value['id'] = '2'
        self.bdb_connection.configure_mock(**{'transactions.retrieve.return_value': self.return_value,
                                              'transactions.prepare.return_value': self.return_value,
                                              'transactions.fulfill.return_value': self.return_value,
                                              'transactions.send.return_value': negative_return,
                                              })
        # asset = {'data': {'prov': account._create_instance_document().serialize(format='json')}}
        with self.assertRaises(exceptions.CreateRecordException):
            account.save_instance_asset(self.bdb_connection)
        # self.bdb_connection.transactions.prepare.assert_called_with(operation='CREATE', signers=account.public_key, asset=asset, metadata={'account_id':str(self.prov_element.identifier)})
        self.bdb_connection.transactions.fulfill.assert_called_with(self.return_value, private_keys=account.private_key)
        self.bdb_connection.transactions.send.assert_called_with(self.return_value)
        self.assertEqual(account.tx_id, '')

    @unittest.skip("testing skipping")
    def test_save_relations_assets(self):
        raise NotImplementedError()

    @unittest.skip("testing skipping")
    def test__create_instance_document(self):
        raise NotImplementedError()

    @unittest.skip("testing skipping")
    def test__create_relations_document(self):
        raise NotImplementedError()

