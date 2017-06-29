import logging
import unittest
from unittest import mock

import prov
from bigchaindb_driver import exceptions as bdb_exceptions

from prov2bigchaindb.core import utils, exceptions
from prov2bigchaindb.tests.core import setup_test_files

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class UtilityTest(unittest.TestCase):
    def setUp(self):
        self.test_prov_files = setup_test_files()
        self.account_id = 'Utility_Test_Account'

    def tearDown(self):
        del self.account_id
        del self.test_prov_files

    def test_to_provdocument(self):
        doc = prov.model.ProvDocument()
        doc.add_namespace('ex', 'http://example.org/')
        doc.entity('ex:foo')
        doc.agent('ex:Bob')
        doc.wasAttributedTo('ex:foo', 'ex:Bob')
        # test json
        prov_document = utils.to_prov_document(content=doc.serialize(format='json'))
        self.assertEqual(doc, prov_document)
        with self.assertRaises(exceptions.ParseException):
            utils.to_prov_document(content="{fooo")
        # test xml
        prov_document = utils.to_prov_document(content=doc.serialize(format='xml'))
        self.assertEqual(doc, prov_document)
        with self.assertRaises(exceptions.ParseException):
            utils.to_prov_document(content="<?xml")
        # test bytes
        content = self.test_prov_files["simple"]
        doc = prov.model.ProvDocument.deserialize(content=content, format='json').flattened()
        prov_document = utils.to_prov_document(content=self.test_prov_files["simple"])
        self.assertEqual(doc, prov_document)
        # test provn (not implement yet by prov)
        with self.assertRaises(NotImplementedError):
            utils.to_prov_document(content=doc.serialize(format='provn'))
        # test invalid document
        with self.assertRaises(exceptions.ParseException):
            utils.to_prov_document(content="fooo")

    @mock.patch('prov2bigchaindb.core.utils.BigchainDB')
    def test_wait_until_valid(self, mock_bdb):
        mock_bdb.transactions.retrieve.return_value = {'id': '1', 'asset': {
            'data': {'prov': ''}}}
        mock_bdb.transactions.status.return_value = {'status': 'valid'}
        utils.wait_until_valid('1', mock_bdb)
        mock_bdb.transactions.status.assert_called_once_with('1')
        mock_bdb.transactions.status.side_effect = bdb_exceptions.NotFoundError()
        with self.assertRaises(exceptions.TransactionIdNotFound):
            utils.wait_until_valid('1', mock_bdb)

    @mock.patch('prov2bigchaindb.core.utils.BigchainDB')
    def test_is_valid_tx(self, mock_bdb):
        mock_bdb.transactions.status.return_value = {'status': 'valid'}
        ret = utils.is_valid_tx('1', mock_bdb)
        mock_bdb.transactions.status.assert_called_once_with('1')
        self.assertEqual(ret, True)
        mock_bdb.transactions.status.return_value = {'status': 'backlog'}
        ret = utils.is_valid_tx('1', mock_bdb)
        self.assertEqual(ret, False)
        mock_bdb.transactions.status.return_value = {'status': 'undecided'}
        ret = utils.is_valid_tx('1', mock_bdb)
        self.assertEqual(ret, False)
        mock_bdb.transactions.status.side_effect = bdb_exceptions.NotFoundError()
        with self.assertRaises(exceptions.TransactionIdNotFound):
            utils.is_valid_tx('1', mock_bdb)

    @mock.patch('prov2bigchaindb.core.utils.BigchainDB')
    @mock.patch('prov2bigchaindb.core.utils.requests.models.Response')
    @mock.patch('prov2bigchaindb.core.utils.requests')
    @mock.patch('prov2bigchaindb.core.utils.random')
    def test_is_block_to_tx_valid(self, mock_random, mock_requests, mock_response, mock_bdb):
        mock_random.choice.return_value = 'http://127.0.0.1:9984'
        mock_response.json.side_effect = [['1'], {'status': 'valid'},
                                          ['1'], {'status': 'undecided'},
                                          ['1'], {'status': 'invalid'},
                                          [],
                                          ['1']]
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response
        ret = utils.is_block_to_tx_valid('1', mock_bdb)
        self.assertEqual(ret, True)
        ret = utils.is_block_to_tx_valid('1', mock_bdb)
        self.assertEqual(ret, False)
        ret = utils.is_block_to_tx_valid('1', mock_bdb)
        self.assertEqual(ret, False)
        with self.assertRaises(exceptions.TransactionIdNotFound):
            utils.is_block_to_tx_valid('1', mock_bdb)
        mock_response.status_code = 400
        with self.assertRaises(exceptions.BlockIdNotFound):
            utils.is_block_to_tx_valid('1', mock_bdb)
