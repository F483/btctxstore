#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals
import json
import binascii
import unittest
from pycoin.key import validate
from btctxstore import BtcTxStore
from btctxstore import exceptions


fixtures = json.load(open("tests/fixtures.json"))


class TestIO(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_readwrite_nulldata(self):
        rawtx = self.api.createtx([],[])
        rawtx = self.api.addnulldata(rawtx, "f483")
        data = self.api.getnulldata(rawtx)
        self.assertEqual(data, "f483")
    
    def test_readwrite_hash160data(self):
        rawtx = self.api.createtx([],[])
        rawtx = self.api.addhash160data(rawtx, 10 * "f483")
        data = self.api.gethash160data(rawtx, 0)
        self.assertEqual(data, 10 * "f483")

    def test_only_one_nulldata_output(self):
        def callback():
            rawtx = self.api.createtx([],[])
            rawtx = self.api.addnulldata(rawtx, "f483")
            self.api.addnulldata(rawtx, "f483")  # writing second fails
        self.assertRaises(exceptions.ExistingNulldataOutput, callback)


class TestCreateTx(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_createtx(self):
        locktime = 0
        txins = fixtures["createtx"]["txins"]
        txouts = fixtures["createtx"]["txouts"]
        expected = fixtures["createtx"]["expected"]
        result = self.api.createtx(txins, txouts, locktime)
        self.assertEqual(result, expected)


class TestCreateKey(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_createkey(self):
        wif = self.api.createkey()
        self.assertTrue(validate.is_wif_valid(wif, allowable_netcodes=['XTN']))


class TestRetrieveTx(unittest.TestCase):

    def test_retrievetx_testnet(self):
        api = BtcTxStore(dryrun=True, testnet=True)
        txid = fixtures["retrievetx"]["testnet"]["txid"]
        expected = fixtures["retrievetx"]["testnet"]["expected"]
        result = api.retrievetx(txid)
        self.assertEqual(result, expected)

    def test_retrievetx_mainnet(self):
        api = BtcTxStore(dryrun=True, testnet=False)
        txid = fixtures["retrievetx"]["mainnet"]["txid"]
        expected = fixtures["retrievetx"]["mainnet"]["expected"]
        result = api.retrievetx(txid)
        self.assertEqual(result, expected)


class TestGetUtxos(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_getutxos(self):
        address = fixtures["wallet"]["address"]
        expected = fixtures["getutxos"]["expected"]
        result = self.api.retrieveutxos([address])
        self.assertEqual(result, expected)


class TestSignTx(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_signtx(self):
        txins = fixtures["signtx"]["txins"]
        txouts = fixtures["signtx"]["txouts"]
        wifs = fixtures["signtx"]["wifs"]
        expected = fixtures["signtx"]["expected"]
        rawtx = self.api.createtx(txins, txouts)
        rawtx = self.api.addnulldata(rawtx, "f483")
        result = self.api.signtx(rawtx, wifs)
        self.assertEqual(result, expected)


class TestStoreNulldata(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_storenulldata_alpha(self):
        wifs = fixtures["storenulldata"]["alpha"]["wifs"]
        result = self.api.storenulldata("f483", wifs)
        expected = fixtures["storenulldata"]["alpha"]["expected"]
        self.assertEqual(result, expected)

    def test_storenulldata_beta(self):
        wifs = fixtures["storenulldata"]["beta"]["wifs"]
        expected = fixtures["storenulldata"]["beta"]["expected"]
        data = binascii.hexlify(b"github.com/F483/btctxstore")
        result = self.api.storenulldata(data, wifs)
        self.assertEqual(result, expected)

    def test_storenulldata_insufficient_funds(self):
        wifs = fixtures["storenulldata"]["insufficient_funds"]["wifs"]
        data = binascii.hexlify(b"f483")

        def callback():
            self.api.storenulldata(data, wifs)
        self.assertRaises(exceptions.InsufficientFunds, callback)

    def test_storenulldata_txouts(self):
        wifs = fixtures["storenulldata"]["txouts"]["wifs"]
        txouts = fixtures["storenulldata"]["txouts"]["txouts"]
        expected = fixtures["storenulldata"]["txouts"]["expected"]
        result = self.api.storenulldata("f483", wifs, txouts=txouts)
        self.assertEqual(result, expected)

    def test_storenulldata_changeaddress(self):
        _fixtures = fixtures["storenulldata"]["changeaddress"]
        wifs = _fixtures["wifs"]
        changeaddress = _fixtures["changeaddress"]
        expected = _fixtures["expected"]
        result = self.api.storenulldata("f483", wifs, changeaddress)
        self.assertEqual(result, expected)


class TestRetrieve(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_retrieve(self):
        txid = fixtures["retrieve"]["nulldata_txid"]
        result = self.api.retrievenulldata(txid)
        self.assertEqual(result, "f483")

    def test_retrieve_nothing(self):
        def callback():
            txid = fixtures["retrieve"]["nonulldata_txid"]
            result = self.api.retrievenulldata(txid)
        self.assertRaises(exceptions.NoNulldataOutput, callback)


class TestGetAddress(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_getaddress(self):
        wif = fixtures["wallet"]["wif"]
        result = self.api.getaddress(wif)
        expected = fixtures["wallet"]["address"]
        self.assertEqual(result, expected)


class TestVerifySignature(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_verify_positive(self):
        _fixtures = fixtures["verifysignature"]["positive"]
        address = _fixtures["address"]
        signature = _fixtures["signature"]
        data = binascii.hexlify(b"testmessage")
        result = self.api.verifysignature(address, signature, data)
        self.assertEqual(result, True)

    def test_verify_incorrect_address(self):
        _fixtures = fixtures["verifysignature"]["incorrect_address"]
        address = _fixtures["address"]
        signature = _fixtures["signature"]
        data = binascii.hexlify(b"testmessage")
        result = self.api.verifysignature(address, signature, data)
        self.assertEqual(result, False)

    def test_verify_incorrect_signature(self):
        _fixtures = fixtures["verifysignature"]["incorrect_signature"]
        address = _fixtures["address"]
        signature = _fixtures["signature"]
        data = binascii.hexlify(b"testmessage")
        result = self.api.verifysignature(address, signature, data)
        self.assertEqual(result, False)

    def test_verify_incorrect_data(self):
        _fixtures = fixtures["verifysignature"]["incorrect_data"]
        address = _fixtures["address"]
        signature = _fixtures["signature"]
        data = binascii.hexlify(b"testmessagee")
        result = self.api.verifysignature(address, signature, data)
        self.assertEqual(result, False)

    def test_verify_signature_params(self):
        wif = "cSuT2J14dYbe1zvB5z5WTXeRcMbj4tnoKssAK1ZQbnX5HtHfW3bi"
        data = binascii.hexlify(b"testmessage")
        address = self.api.getaddress(wif)
        sig = "///////////////////////////////////////////////////////////////////////////////////////="
        self.assertFalse(self.api.verifysignature(address, sig, data))


class TestSignData(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_sign_a(self):
        wif = fixtures["wallet"]["wif"]
        data = binascii.hexlify(b"testmessage")
        address = self.api.getaddress(wif)
        sig = self.api.signdata(wif, data)
        valid = self.api.verifysignature(address, sig, data)
        self.assertEqual(valid, True)

    def test_sign_b(self):
        wif = "cSuT2J14dYbe1zvB5z5WTXeRcMbj4tnoKssAK1ZQbnX5HtHfW3bi"
        data = binascii.hexlify(b"testmessage")
        address = self.api.getaddress(wif)
        sig = self.api.signdata(wif, data)
        valid = self.api.verifysignature(address, sig, data)
        self.assertEqual(valid, True)


class TestSplitUtxos(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_singleinput(self):
        wif = "cNHPbjVpkv4oqqKimBNp1UfQ2dhjETtRZw4KkHWtPgnU36SBtXub"
        # address n4RHA7mxH8EYV7wMS8evtYRYwCpQYz6KuE
        txids = self.api.splitutxos(wif, 10000000)  # 100mBTC
        print("TestSplitUtxos txids:", len(txids))
        self.assertEqual(len(txids), 1)

    def test_manyinputs(self):
        wif = "cRoboMG5KM19VP8ZcVCDXGCfi1JJraKpw58ofe8v57j7vqDxaQ5m"
        # address mqox6abLAiado9kFvX3EsHaVFbYVimSMCK
        txids = self.api.splitutxos(wif, 100000)  # 1mBTC
        print("TestSplitUtxos txids:", len(txids))
        self.assertEqual(len(txids), 6)


if __name__ == '__main__':
    unittest.main()
