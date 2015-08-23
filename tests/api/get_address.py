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


S_WIF = "92JATRBTHRGAACcJb41dAGnh7kQ1wev27tcYWcGA2RZeUJLCcZo"
B_WIF = b"92JATRBTHRGAACcJb41dAGnh7kQ1wev27tcYWcGA2RZeUJLCcZo"
U_WIF = u"92JATRBTHRGAACcJb41dAGnh7kQ1wev27tcYWcGA2RZeUJLCcZo"
EXPECTED = "n3mW3o8XNMyH6xHWBkN98rm7zxxxswzpGM"


class TestGetAddress(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_standard(self):
        wif = self.api.create_key()
        address = self.api.get_address(wif)
        self.assertTrue(validate.is_address_valid(address, allowable_netcodes=['XTN']))

    def test_input_validation(self):

        # test correct types
        a = self.api.get_address(S_WIF)
        b = self.api.get_address(B_WIF)
        c = self.api.get_address(U_WIF)
        self.assertEqual(a, b, c)

        # TODO invalid types
        # TODO invalid input data

    def test_standards_compliant(self):
        wif = self.api.create_key()
        address = self.api.get_address(S_WIF)
        self.assertEqual(address, EXPECTED)
        # FIXME verify 3rd party produces this address


if __name__ == '__main__':
    unittest.main()
