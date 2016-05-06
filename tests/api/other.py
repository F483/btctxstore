#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals
import json
import binascii
import unittest
from btctxstore import BtcTxStore
from btctxstore import exceptions
fixtures = json.load(open("tests/fixtures.json"))


class TestAddInputs(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    # TODO test signing

    def test_add_inputs_withchange(self):
        txouts = fixtures["add_inputs"]["withchange"]["txouts"]
        wifs = fixtures["add_inputs"]["withchange"]["wifs"]
        change_address = fixtures["add_inputs"]["withchange"]["change_address"]
        expected = fixtures["add_inputs"]["withchange"]["expected"]
        rawtx = self.api.create_tx(txouts=txouts)
        result = self.api.add_inputs(rawtx, wifs, change_address,
                                     dont_sign=True)
        self.assertEqual(expected, result)

    def test_add_inputs_nochange(self):
        txouts = fixtures["add_inputs"]["nochange"]["txouts"]
        wifs = fixtures["add_inputs"]["nochange"]["wifs"]
        expected = fixtures["add_inputs"]["nochange"]["expected"]
        rawtx = self.api.create_tx(txouts=txouts)
        result = self.api.add_inputs(rawtx, wifs, dont_sign=True)
        self.assertEqual(expected, result)


class TestIO(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_readwrite_nulldata(self):
        rawtx = self.api.create_tx()
        rawtx = self.api.add_nulldata(rawtx, "f483")
        data = self.api.get_nulldata(rawtx)
        self.assertEqual(data, "f483")

    def test_readwrite_hash160data(self):
        rawtx = self.api.create_tx()
        rawtx = self.api.add_hash160data(rawtx, 10 * "f483")
        data = self.api.get_hash160data(rawtx, 0)
        self.assertEqual(data, 10 * "f483")

    def test_readwrite_data_blob(self):
        rawtx = self.api.create_tx()
        data_in = "f483" * 30 + "beef" * 30
        rawtx = self.api.add_data_blob(rawtx, data_in)
        data_out = self.api.get_data_blob(rawtx)
        self.assertEqual(data_in, data_out)

    def test_readwrite_broadcast_message(self):
        message = u"Ünicode test massage"
        sender_wif = fixtures["wallet"]["wif"]
        sender_address = fixtures["wallet"]["address"]
        sender_hash160hex = fixtures["wallet"]["hash160hex"]

        # create broadcast message tx
        rawtx = self.api.create_tx()
        rawtx = self.api.add_broadcast_message(rawtx, message, sender_wif)

        # check that sender address is aligned so its visible in history
        hash160hex = self.api.get_hash160data(rawtx, 3)
        self.assertEqual(hash160hex, sender_hash160hex)

        # get broadcast message from tx
        result = self.api.get_broadcast_message(rawtx)
        self.assertEqual(result["address"], sender_address)
        self.assertEqual(result["message"], message)

        # check signature is valid
        hex_message = binascii.hexlify(result["message"].encode('utf-8'))
        valid_signature = self.api.verify_signature(result["address"],
                                                    result["signature"],
                                                    hex_message)
        self.assertTrue(valid_signature)

    def test_only_one_nulldata_output(self):
        def callback():
            rawtx = self.api.create_tx()
            rawtx = self.api.add_nulldata(rawtx, "f483")
            self.api.add_nulldata(rawtx, "f483")  # writing second fails
        self.assertRaises(exceptions.ExistingNulldataOutput, callback)


class TestCreateTx(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_create_tx(self):
        lock_time = 0
        txins = fixtures["create_tx"]["txins"]
        txouts = fixtures["create_tx"]["txouts"]
        expected = fixtures["create_tx"]["expected"]
        result = self.api.create_tx(txins, txouts, lock_time)
        self.assertEqual(result, expected)


class TestRetrieveTx(unittest.TestCase):

    def test_retrieve_tx_testnet(self):
        api = BtcTxStore(dryrun=True, testnet=True)
        txid = fixtures["retrieve_tx"]["testnet"]["txid"]
        expected = fixtures["retrieve_tx"]["testnet"]["expected"]
        result = api.retrieve_tx(txid)
        self.assertEqual(result, expected)

    def test_retrieve_tx_mainnet(self):
        api = BtcTxStore(dryrun=True, testnet=False)
        txid = fixtures["retrieve_tx"]["mainnet"]["txid"]
        expected = fixtures["retrieve_tx"]["mainnet"]["expected"]
        result = api.retrieve_tx(txid)
        self.assertEqual(result, expected)


class TestGetUtxos(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_getutxos(self):
        address = fixtures["wallet"]["address"]
        expected = fixtures["getutxos"]["expected"]
        result = self.api.retrieve_utxos([address])
        self.assertEqual(result, expected)


class TestSignTx(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_sign_tx(self):
        txins = fixtures["sign_tx"]["txins"]
        txouts = fixtures["sign_tx"]["txouts"]
        wifs = fixtures["sign_tx"]["wifs"]
        expected = fixtures["sign_tx"]["expected"]
        rawtx = self.api.create_tx(txins, txouts)
        rawtx = self.api.add_nulldata(rawtx, "f483")
        result = self.api.sign_tx(rawtx, wifs)
        self.assertEqual(result, expected)


class TestStoreNulldata(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_store_nulldata_alpha(self):
        wifs = fixtures["store_nulldata"]["alpha"]["wifs"]
        result = self.api.store_nulldata("f483", wifs)
        expected = fixtures["store_nulldata"]["alpha"]["expected"]
        self.assertEqual(result, expected)

    def test_store_nulldata_beta(self):
        wifs = fixtures["store_nulldata"]["beta"]["wifs"]
        expected = fixtures["store_nulldata"]["beta"]["expected"]
        data = binascii.hexlify(b"github.com/F483/btctxstore")
        result = self.api.store_nulldata(data, wifs)
        self.assertIn(result, expected)

    def test_store_nulldata_insufficient_funds(self):
        wifs = fixtures["store_nulldata"]["insufficient_funds"]["wifs"]
        data = binascii.hexlify(b"f483")

        def callback():
            self.api.store_nulldata(data, wifs)
        self.assertRaises(exceptions.InsufficientFunds, callback)

    def test_store_nulldata_txouts(self):
        wifs = fixtures["store_nulldata"]["txouts"]["wifs"]
        txouts = fixtures["store_nulldata"]["txouts"]["txouts"]
        expected = fixtures["store_nulldata"]["txouts"]["expected"]
        result = self.api.store_nulldata("f483", wifs, txouts=txouts)
        self.assertEqual(result, expected)

    def test_store_nulldata_change_address(self):
        _fixtures = fixtures["store_nulldata"]["change_address"]
        wifs = _fixtures["wifs"]
        change_address = _fixtures["change_address"]
        expected = _fixtures["expected"]
        result = self.api.store_nulldata("f483", wifs, change_address)
        self.assertEqual(result, expected)


class TestRetrieve(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_retrieve(self):
        txid = fixtures["retrieve"]["nulldata_txid"]
        result = self.api.retrieve_nulldata(txid)
        self.assertEqual(result, "f483")

    def test_retrieve_nothing(self):
        def callback():
            txid = fixtures["retrieve"]["nonulldata_txid"]
            self.api.retrieve_nulldata(txid)
        self.assertRaises(exceptions.NoNulldataOutput, callback)


class TestSignData(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_sign_a(self):
        wif = fixtures["wallet"]["wif"]
        data = binascii.hexlify(b"testmessage")
        address = self.api.get_address(wif)
        sig = self.api.sign_data(wif, data)
        valid = self.api.verify_signature(address, sig, data)
        self.assertEqual(valid, True)

    def test_sign_b(self):
        wif = "cSuT2J14dYbe1zvB5z5WTXeRcMbj4tnoKssAK1ZQbnX5HtHfW3bi"
        data = binascii.hexlify(b"testmessage")
        address = self.api.get_address(wif)
        sig = self.api.sign_data(wif, data)
        valid = self.api.verify_signature(address, sig, data)
        self.assertEqual(valid, True)


class TestSignUnicode(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_sign_a(self):
        wif = fixtures["wallet"]["wif"]
        message = u"üöä"
        address = self.api.get_address(wif)
        sig = self.api.sign_unicode(wif, message)
        valid = self.api.verify_signature_unicode(address, sig, message)
        self.assertEqual(valid, True)

    def test_sign_b(self):
        wif = "cSuT2J14dYbe1zvB5z5WTXeRcMbj4tnoKssAK1ZQbnX5HtHfW3bi"
        message = u"üöä"
        address = self.api.get_address(wif)
        sig = self.api.sign_unicode(wif, message)
        valid = self.api.verify_signature_unicode(address, sig, message)
        self.assertEqual(valid, True)


class TestSplitUtxos(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_singleinput(self):
        wif = "cNHPbjVpkv4oqqKimBNp1UfQ2dhjETtRZw4KkHWtPgnU36SBtXub"
        # address n4RHA7mxH8EYV7wMS8evtYRYwCpQYz6KuE
        txids = self.api.split_utxos(wif, 10000000)  # 100mBTC
        self.assertEqual(len(txids), 1)

    def test_manyinputs(self):
        wif = "cRoboMG5KM19VP8ZcVCDXGCfi1JJraKpw58ofe8v57j7vqDxaQ5m"
        # address mqox6abLAiado9kFvX3EsHaVFbYVimSMCK
        txids = self.api.split_utxos(wif, 100000)  # 1mBTC
        self.assertEqual(len(txids), 6)


class TestValidateAddressTestnet(unittest.TestCase):

    def setUp(self):
        self.testnet_api = BtcTxStore(dryrun=True, testnet=True)
        self.mainnet_api = BtcTxStore(dryrun=True, testnet=False)

    def test_valid_string(self):
        address = 'migiScBNvVKYwEiCFhgBNGtZ87cdygtuSQ'
        self.assertTrue(self.testnet_api.validate_address(address))

    def test_valid_network(self):
        address = self.testnet_api.get_address(self.testnet_api.create_key())
        self.assertTrue(self.testnet_api.validate_address(address))

    def test_invalid_network(self):
        address = self.mainnet_api.get_address(self.mainnet_api.create_key())
        self.assertFalse(self.testnet_api.validate_address(address))

    def test_invalid_data(self):
        self.assertFalse(self.testnet_api.validate_address("f483"))

    def test_invalid_type(self):
        self.assertFalse(self.testnet_api.validate_address(None))


class TestValidateAddressMainnet(unittest.TestCase):

    def setUp(self):
        self.testnet_api = BtcTxStore(dryrun=True, testnet=True)
        self.mainnet_api = BtcTxStore(dryrun=True, testnet=False)

    def test_valid_string(self):
        address = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        self.assertTrue(self.mainnet_api.validate_address(address))

    def test_valid_network(self):
        address = self.mainnet_api.get_address(self.mainnet_api.create_key())
        self.assertTrue(self.mainnet_api.validate_address(address))

    def test_invalid_network(self):
        address = self.testnet_api.get_address(self.testnet_api.create_key())
        self.assertFalse(self.mainnet_api.validate_address(address))

    def test_invalid_data(self):
        self.assertFalse(self.mainnet_api.validate_address("f483"))

    def test_invalid_type(self):
        self.assertFalse(self.mainnet_api.validate_address(None))


class TestValidateKeyTestnet(unittest.TestCase):

    def setUp(self):
        self.testnet_api = BtcTxStore(dryrun=True, testnet=True)
        self.mainnet_api = BtcTxStore(dryrun=True, testnet=False)

    def test_valid_network(self):
        key = self.testnet_api.create_key()
        self.assertTrue(self.testnet_api.validate_key(key))

    def test_invalid_network(self):
        key = self.mainnet_api.create_key()
        self.assertFalse(self.testnet_api.validate_key(key))

    def test_invalid_data(self):
        self.assertFalse(self.testnet_api.validate_key("f483"))

    def test_invalid_type(self):
        self.assertFalse(self.testnet_api.validate_key(None))


class TestValidateKeyMainnet(unittest.TestCase):

    def setUp(self):
        self.testnet_api = BtcTxStore(dryrun=True, testnet=True)
        self.mainnet_api = BtcTxStore(dryrun=True, testnet=False)

    def test_valid_network(self):
        key = self.mainnet_api.create_key()
        self.assertTrue(self.mainnet_api.validate_key(key))

    def test_invalid_network(self):
        key = self.testnet_api.create_key()
        self.assertFalse(self.mainnet_api.validate_key(key))

    def test_invalid_data(self):
        self.assertFalse(self.mainnet_api.validate_key("f483"))

    def test_invalid_type(self):
        self.assertFalse(self.mainnet_api.validate_key(None))


if __name__ == '__main__':
    unittest.main()
