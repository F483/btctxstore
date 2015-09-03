#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals
import unittest
from btctxstore import exceptions
from btctxstore import BtcTxStore


S_HWIF = "tprv8ZgxMBicQKsPeFZuyoMy197pX8iJeTasLVYEeb68cj489fmCz7kxP8vAfJp3rWebDT3nLvDsBaz3CqnUfdhr1wbjmhUNwK5Hf7dN2Er9btD"
B_HWIF = b"tprv8ZgxMBicQKsPeFZuyoMy197pX8iJeTasLVYEeb68cj489fmCz7kxP8vAfJp3rWebDT3nLvDsBaz3CqnUfdhr1wbjmhUNwK5Hf7dN2Er9btD"
U_HWIF = u"tprv8ZgxMBicQKsPeFZuyoMy197pX8iJeTasLVYEeb68cj489fmCz7kxP8vAfJp3rWebDT3nLvDsBaz3CqnUfdhr1wbjmhUNwK5Hf7dN2Er9btD"


class TestValidateWallet(unittest.TestCase):

    def setUp(self):
        self.testnet_api = BtcTxStore(dryrun=True, testnet=True)
        self.mainnet_api = BtcTxStore(dryrun=True, testnet=False)
        self.testnet_wallet = self.testnet_api.create_wallet()
        self.mainnet_wallet = self.mainnet_api.create_wallet()
        self.testnet_key = self.testnet_api.get_key(self.testnet_wallet)
        self.mainnet_key = self.mainnet_api.get_key(self.mainnet_wallet)

    def test_checks_networks(self):
        self.assertTrue(self.testnet_api.validate_wallet(self.testnet_wallet))
        self.assertTrue(self.mainnet_api.validate_wallet(self.mainnet_wallet))
        self.assertFalse(self.testnet_api.validate_wallet(self.mainnet_wallet))
        self.assertFalse(self.mainnet_api.validate_wallet(self.testnet_wallet))

    def test_doesnt_validate_keys(self):
        self.assertFalse(self.testnet_api.validate_wallet(self.testnet_key))
        self.assertFalse(self.mainnet_api.validate_wallet(self.testnet_key))
        self.assertFalse(self.testnet_api.validate_wallet(self.mainnet_key))
        self.assertFalse(self.mainnet_api.validate_wallet(self.mainnet_key))

    def test_correct_types(self):
        self.assertTrue(self.testnet_api.validate_wallet(S_HWIF))
        self.assertTrue(self.testnet_api.validate_wallet(B_HWIF))
        self.assertTrue(self.testnet_api.validate_wallet(U_HWIF))


if __name__ == '__main__':
    unittest.main()
