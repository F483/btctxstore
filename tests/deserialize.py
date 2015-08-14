#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals
import unittest
from btctxstore import deserialize
from btctxstore import exceptions


class TestNulldataTxOut(unittest.TestCase):

    def test_max_data(self):

        # fourty bytes ok
        max_data = 40 * b"aa"
        deserialize.nulldata_txout(max_data)

        # > fourty bytes fails
        def callback():
            over_max_data = 41 * b"aa"
            deserialize.nulldata_txout(over_max_data)
        self.assertRaises(exceptions.MaxNulldataExceeded, callback)


class TestHash160DataTxOut(unittest.TestCase):

    def test_data_size(self):

        # twenty bytes ok
        max_data = 20 * b"aa"
        deserialize.hash160data_txout(max_data)

        # > twenty bytes fails
        def callback():
            over_max_data = 21 * b"aa"
            deserialize.hash160data_txout(over_max_data)
        self.assertRaises(exceptions.InvalidHash160DataSize, callback)

        # < twenty bytes fails
        def callback():
            over_max_data = 19 * b"aa"
            deserialize.hash160data_txout(over_max_data)
        self.assertRaises(exceptions.InvalidHash160DataSize, callback)


class TestKey(unittest.TestCase):

    def test_invalid_netcode(self):
        testnet_wif = "cNf7CMEHfD2jLtiTASbCAEneVnVmD4syA4A9KhUXqAkRs26Ke6xw"
        mainnet_wif = "KzU3561hXZwFPrzmHkJ6FLWvykFJMQnMEwSKXW5VPpz6HcxuvpZq"

        # test positive
        deserialize.key(True, testnet_wif)  # testnet
        deserialize.key(False, mainnet_wif)  # mainnet

        # testnet negative
        def callback():
            deserialize.key(False, testnet_wif)
        self.assertRaises(exceptions.InvalidWif, callback)

        # mainnet negative
        def callback():
            deserialize.key(True, mainnet_wif)
        self.assertRaises(exceptions.InvalidWif, callback)

        # testnet non string
        def callback():
            deserialize.key(False, None)
        self.assertRaises(exceptions.InvalidInput, callback)

        # mainnet non string
        def callback():
            deserialize.key(True, None)
        self.assertRaises(exceptions.InvalidInput, callback)

        # testnet garbage string
        def callback():
            deserialize.key(False, "garbage")
        self.assertRaises(exceptions.InvalidWif, callback)

        # mainnet garbage string
        def callback():
            deserialize.key(True, "garbage")
        self.assertRaises(exceptions.InvalidWif, callback)


class TestAddress(unittest.TestCase):

    def test_invalid_netcode(self):
        testnet_address = "mgBJ5bG9mQw8mHHcVEJghMamQEXeNLtvpt"
        mainnet_address = "1BTF7gU1EmgasGh85ypacDvsVKg4weZMfz"

        # testnet positive
        address = deserialize.address(True, testnet_address)
        self.assertEqual(testnet_address, address)

        # mainnet positive
        address = deserialize.address(False, mainnet_address)
        self.assertEqual(mainnet_address, address)

        # testnet negative
        def callback():
            deserialize.address(False, testnet_address)
        self.assertRaises(exceptions.InvalidAddress, callback)

        # mainnet negative
        def callback():
            deserialize.address(True, mainnet_address)
        self.assertRaises(exceptions.InvalidAddress, callback)

        # non string testnet
        def callback():
            deserialize.address(False, None)
        self.assertRaises(exceptions.InvalidInput, callback)

        # non string mainnet
        def callback():
            deserialize.address(True, None)
        self.assertRaises(exceptions.InvalidInput, callback)

        # garbage string testnet
        def callback():
            deserialize.address(False, "garbage")
        self.assertRaises(exceptions.InvalidAddress, callback)

        # garbage string mainnet
        def callback():
            deserialize.address(True, "garbage")
        self.assertRaises(exceptions.InvalidAddress, callback)
