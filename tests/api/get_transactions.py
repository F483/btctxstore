#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals
import unittest
from btctxstore import BtcTxStore


class TestGetTransactions(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_used(self):
        address = "2MwYLBKhvqezurTWsyzFRbA3BG2fYLmTTDK"
        transactions = self.api.get_transactions(address)
        self.assertEqual(transactions, [
            "5599b00529a82dd5957be87681fb9da07ef54665ca8621f636a2a6ccd949a8c6",
            "64754ea8ab2b42cedb95a1548d83e166b03c350fe21044be411b07a36ec66ebd"
        ])

    def test_unused(self):
        address = "mwacg9L7raork91AP6wiZpA291bATguX47"
        transactions = self.api.get_transactions(address)
        self.assertEqual(transactions, [])


if __name__ == '__main__':
    unittest.main()
