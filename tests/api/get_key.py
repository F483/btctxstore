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


class TestGetWalletKey(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_standard(self):
        hwif = self.api.create_wallet()
        wif = self.api.get_key(hwif)
        self.assertTrue(validate.is_wif_valid(wif, allowable_netcodes=['XTN']))

    def test_input_validation(self):
        pass
        # TODO test valid types "", b"", u""
        # TODO invalid types
        # TODO wrong data keys, addresses, txids, other garbage


if __name__ == '__main__':
    unittest.main()
