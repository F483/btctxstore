#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


import unittest
from btctxstore import BtcTxStore


unsignedrawtx = "0100000001ef5b2eb4b9b0c10449cbabedca45709135d457a04dabd33c1068aaf86562a72b0200000000ffffffff0240420f00000000001976a91491cc9812ca45e7209ff9364ce96527a7c49f1f3188ac3e770400000000001976a9142e330c36e1d0f199fd91446f2210209a0d35caef88ac00000000"


class TestIO(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(testnet=True)

    def test_readwrite(self):
        outputtx = self.api.writebin(unsignedrawtx, "f483")
        data = self.api.readbin(outputtx)
        self.assertEquals(data, "f483")

    def test_only_one_nulldata_output(self):
        def callback():
            outputtx = self.api.writebin(unsignedrawtx, "f483")
            self.api.writebin(outputtx, "f483")
        self.assertRaises(Exception, callback)

    def test_max_data(self):
        max_data = 40 * "aa" # fourty bytes
        self.api.writebin(unsignedrawtx, max_data)
        def callback():
            over_max_data = 41 * "aa" # fourty bytes
            self.api.writebin(unsignedrawtx, over_max_data)
        self.assertRaises(Exception, callback)


class TestNewRawtx(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(testnet=True)

    def test_create(self):
        txins = """[
            {
                "txid" : "33a184cba7cf96cc167780561d261201cef0fb424d6591588d88e61bcfdd09c8",
                "index" : 0
            },
            {
                "txid" : "d2f4411e0b29d0f2f4fed66d0e19cef337b2d8fe1a809e4c46833429f6ea87d0",
                "index" : 1
            }
        ]"""
        txouts = """[
            {
                "address" : "migiScBNvVKYwEiCFhgBNGtZ87cdygtuSQ",
                "value" : "750000"
            },
            {
                "address" : "mkSWUYy3ggmbfGMf4PrjKj4LdU45Ytt2DN",
                "value" : "1000104"
            }
        ]"""
        locktime = 0
        testnet = True
        result = self.api.createtx(txins, txouts, locktime)
        expected = "0100000002c809ddcf1be6888d5891654d42fbf0ce0112261d56807716cc96cfa7cb84a1330000000000ffffffffd087eaf6293483464c9e801afed8b237f3ce190e6dd6fef4f2d0290b1e41f4d20100000000ffffffff02b0710b00000000001976a91422c0f934b5346bd3e14dd47c2eb26c4bdf15eab988aca8420f00000000001976a91436016996a73708c5faa17ac9b76ec380941e545a88ac00000000"
        self.assertEquals(result, expected)




if __name__ == '__main__':
    unittest.main()


