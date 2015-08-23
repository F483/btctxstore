#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals
import unittest
from pycoin.key import validate
from btctxstore import BtcTxStore
from btctxstore import exceptions


S_HWIF = "tprv8ZgxMBicQKsPeFZuyoMy197pX8iJeTasLVYEeb68cj489fmCz7kxP8vAfJp3rWebDT3nLvDsBaz3CqnUfdhr1wbjmhUNwK5Hf7dN2Er9btD"
B_HWIF = b"tprv8ZgxMBicQKsPeFZuyoMy197pX8iJeTasLVYEeb68cj489fmCz7kxP8vAfJp3rWebDT3nLvDsBaz3CqnUfdhr1wbjmhUNwK5Hf7dN2Er9btD"
U_HWIF = u"tprv8ZgxMBicQKsPeFZuyoMy197pX8iJeTasLVYEeb68cj489fmCz7kxP8vAfJp3rWebDT3nLvDsBaz3CqnUfdhr1wbjmhUNwK5Hf7dN2Er9btD"


class TestGetWalletKey(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_standard(self):
        hwif = self.api.create_wallet()
        wif = self.api.get_key(hwif)
        self.assertTrue(validate.is_wif_valid(wif, allowable_netcodes=['XTN']))

    def test_input_validation(self):
        
        # test correct types
        a = self.api.get_key(S_HWIF)
        b = self.api.get_key(B_HWIF)
        c = self.api.get_key(U_HWIF)
        self.assertEqual(a, b, c)

        # TODO invalid types
        # TODO invalid input data

    def test_standards_compliant(self):
        pass # FIXME check generated against expected output from 3rd parties


if __name__ == '__main__':
    unittest.main()
