#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals


import binascii
import unittest
from btctxstore import BtcTxStore
from btctxstore import exceptions


wallet = {
    "wif" : "92JATRBTHRGAACcJb41dAGnh7kQ1wev27tcYWcGA2RZeUJLCcZo",
    "address" : "n3mW3o8XNMyH6xHWBkN98rm7zxxxswzpGM"
}


unsignedrawtx = "0100000001ef5b2eb4b9b0c10449cbabedca45709135d457a04dabd33c1068aaf86562a72b0200000000ffffffff0240420f00000000001976a91491cc9812ca45e7209ff9364ce96527a7c49f1f3188ac3e770400000000001976a9142e330c36e1d0f199fd91446f2210209a0d35caef88ac00000000"


class TestIO(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_readwrite(self):
        rawtx = self.api.addnulldata(unsignedrawtx, "f483")
        data = self.api.getnulldata(rawtx)
        self.assertEqual(data, "f483")

    def test_only_one_nulldata_output(self):
        def callback():
            rawtx = self.api.addnulldata(unsignedrawtx, "f483")
            self.api.addnulldata(rawtx, "f483") # writing second fails
        self.assertRaises(exceptions.ExistingNulldataOutput, callback)


class TestCreateTx(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_create(self):
        txins = [
            {
                "txid" : "33a184cba7cf96cc167780561d261201cef0fb424d6591588d88e61bcfdd09c8",
                "index" : 0
            },
            {
                "txid" : "d2f4411e0b29d0f2f4fed66d0e19cef337b2d8fe1a809e4c46833429f6ea87d0",
                "index" : 1
            }
        ]
        txouts = [
            {
                "address" : "migiScBNvVKYwEiCFhgBNGtZ87cdygtuSQ",
                "value" : "750000"
            },
            {
                "address" : "mkSWUYy3ggmbfGMf4PrjKj4LdU45Ytt2DN",
                "value" : "1000104"
            }
        ]
        locktime = 0
        testnet = True
        result = self.api.createtx(txins, txouts, locktime)
        expected = "0100000002c809ddcf1be6888d5891654d42fbf0ce0112261d56807716cc96cfa7cb84a1330000000000ffffffffd087eaf6293483464c9e801afed8b237f3ce190e6dd6fef4f2d0290b1e41f4d20100000000ffffffff02b0710b00000000001976a91422c0f934b5346bd3e14dd47c2eb26c4bdf15eab988aca8420f00000000001976a91436016996a73708c5faa17ac9b76ec380941e545a88ac00000000"
        self.assertEqual(result, expected)


class TestGetTx(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_gettx(self):
        txid = "987451c344c504d07c1fa12cfbf84b5346535da5154006f6dc8399a8fae127eb"
        expected = "0100000001f2963731aa6b1e27a2f94d79620fad643e9e65741b16dadd4e77489c34f20ae2010000008a473044022054d89d41e9a3df9ea6ac367e0a062bd7c65c50232ff36d1f9287cd1851c7444e022069736675af9b94340d64b2b67913c07c4fc2f24006e77ad4df5a13a26e1200350141040319ffdcba35ef3d2577cdf6f07483f4b30865f695d366f02926db1ddd0c03544150b65124baf42601945d1c848bca7970cfa29f538f4ad8cd2564b8f80bb10cffffffff020000000000000000046a02f48370811201000000001976a914f4131906b10615a61af347c56f1223ddc214f95c88ac00000000"
        result = self.api.retrievetx(txid)
        self.assertEqual(result, expected)


class TestGetUtxos(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_getutxos(self):
        address = wallet["address"]
        expected = [{
            "index": 1, 
            "txid": "ba7a0b63c49994006e45449fdf0d39414f0f3473e55d206ccbf994f3a5122722",
            "script": "76a914f4131906b10615a61af347c56f1223ddc214f95c88ac",
            "value": 17980000
        }]
        result = self.api.retrieveutxos([address])
        self.assertEqual(result, expected)


class TestSignTx(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_signtx(self):
        txins = [{
          "index": 1, 
          "txid": "987451c344c504d07c1fa12cfbf84b5346535da5154006f6dc8399a8fae127eb"
        }]
        txouts = [{
          "address" : wallet["address"],
          "value" : 17980000
        }]
        wifs = [wallet["wif"]]
        rawtx = self.api.createtx(txins, txouts)
        rawtx = self.api.addnulldata(rawtx, "f483")
        result = self.api.signtx(rawtx, wifs)
        expected = "0100000001eb27e1faa89983dcf6064015a55d5346534bf8fb2ca11f7cd004c544c3517498010000008b4830450221008326d0d915dd8d3f9bcced2d774f4a898ed2c4a4929a06c7539500ded89e92db02201542ce4beda2eb1cfdefa3d647481a2a2f38231c953bba8efbb860fe1f49981d0141040319ffdcba35ef3d2577cdf6f07483f4b30865f695d366f02926db1ddd0c03544150b65124baf42601945d1c848bca7970cfa29f538f4ad8cd2564b8f80bb10cffffffff02605a1201000000001976a914f4131906b10615a61af347c56f1223ddc214f95c88ac0000000000000000046a02f48300000000"
        self.assertEqual(result, expected)


class TestStore(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_store_a(self):
        wifs = [wallet["wif"]]
        result = self.api.storenulldata("f483", wifs)
        expected = "0a6675f32c20aa74218130210ad817f6e2a55fac0ced8b49516a72a98f47ae81"
        self.assertEqual(result, expected)
    
    def test_store_b(self):
        wifs = ["cUZfG8KJ3BrXneg2LjUX4VoMg76Fcgx6QDiAZj2oGbuw6da8Lzv1"]
        data = binascii.hexlify(b"github.com/F483/btctxstore")
        txid = self.api.storenulldata(data, wifs)
    
    def test_store_insufficient_funds(self):
        wifs = ["cVJKkzZpEuVXvrM7Q5qza9W1zcU39DSFRDMoFmXMa9h7LARGTY7w"]
        data = binascii.hexlify(b"f483")
        def callback():
            self.api.storenulldata(data, wifs)
        self.assertRaises(exceptions.InsufficientFunds, callback)

    def test_store_txouts(self):
        wifs = [wallet["wif"]]
        txouts = [{
          "address" : "mgBJ5bG9mQw8mHHcVEJghMamQEXeNLtvpt",
          "value" : 10000000
        }]
        result = self.api.storenulldata("f483", wifs, txouts=txouts)
        expected = "b5446f2a78e80717c5d75fa3e67d52d3291c42da20c9b02afe27b6403db5906d"
        self.assertEqual(result, expected)

    def test_store_changeaddress(self):
        wifs = [wallet["wif"]]
        changeaddress = "mgBJ5bG9mQw8mHHcVEJghMamQEXeNLtvpt"
        result = self.api.storenulldata("f483", wifs, changeaddress)
        expected = "44048c97399574643edf9db089b7f0f69d173d76a72ab12cc8e4670e6356f7d3"
        self.assertEqual(result, expected)


class TestRetrieve(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_retrieve(self):
        txid = "987451c344c504d07c1fa12cfbf84b5346535da5154006f6dc8399a8fae127eb"
        result = self.api.retrievenulldata(txid)
        self.assertEqual(result, "f483")


class TestGetAddress(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_getaddress(self):
        wif = wallet["wif"]
        result = self.api.getaddress(wif)
        expected = wallet["address"]
        self.assertEqual(result, expected)


class TestVerifySignature(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_verify_positive(self):
        address = "mkRqiCnLFFsEH6ezsE1RiMxEjLRXZzWjwe"
        signature = "H8wq7z8or7jGGT06ZJ0dC1+wnmRLY/fWnW2SRSRPtypaBAFJAtYhcOl+0jyjujEio91/7eFEW9tuM/WZOusSEGc="
        data = binascii.hexlify(b"testmessage")
        result = self.api.verifysignature(address, signature, data)
        self.assertEqual(result, True)

    def test_verify_incorrect_address(self):
        address = "mkRqiCnLFFsEH6ezsE2RiMxEjLRXZzWjwe"
        signature = "H8wq7z8or7jGGT06ZJ0dC1+wnmRLY/fWnW2SRSRPtypaBAFJAtYhcOl+0jyjujEio91/7eFEW9tuM/WZOusSEGc="
        data = binascii.hexlify(b"testmessage")
        result = self.api.verifysignature(address, signature, data)
        self.assertEqual(result, False)

    def test_verify_incorrect_signature(self):
        address = "mkRqiCnLFFsEH6ezsE1RiMxEjLRXZzWjwe"
        signature = "H8wq7z8or7jGGT06ZJ1dC1+wnmRLY/fWnW2SRSRPtypaBAFJAtYhcOl+0jyjujEio91/7eFEW9tuM/WZOusSEGc="
        data = binascii.hexlify(b"testmessage")
        result = self.api.verifysignature(address, signature, data)
        self.assertEqual(result, False)

    def test_verify_incorrect_data(self):
        address = "mkRqiCnLFFsEH6ezsE1RiMxEjLRXZzWjwe"
        signature = "H8wq7z8or7jGGT06ZJ0dC1+wnmRLY/fWnW2SRSRPtypaBAFJAtYhcOl+0jyjujEio91/7eFEW9tuM/WZOusSEGc="
        data = binascii.hexlify(b"testmessagee")
        result = self.api.verifysignature(address, signature, data)
        self.assertEqual(result, False)

    def test_verify_signature_params(self):
        pass # TODO test incorrect signature params (first byte)


class TestSignData(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_sign_a(self):
        wif = wallet["wif"]
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

if __name__ == '__main__':
    unittest.main()


