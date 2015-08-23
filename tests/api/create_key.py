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


class TestCreateKey(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_standard(self):
        wif = self.api.create_key()
        self.assertTrue(validate.is_wif_valid(wif, allowable_netcodes=['XTN']))

    def test_random(self):
        a = self.api.create_key()
        b = self.api.create_key()
        self.assertTrue(a != b)

    def test_master_secret(self):
        a = self.api.create_key(master_secret="foo")
        b = self.api.create_key(master_secret="foo")
        self.assertEqual(a, b)

    def test_input_validation(self):

        # correct types
        a = self.api.create_key(master_secret="foo")
        b = self.api.create_key(master_secret=b"foo")
        c = self.api.create_key(master_secret=u"foo")
        self.assertEqual(a, b, c)
        self.assertTrue(self.api.create_key(master_secret="üöä") != None)
        self.assertTrue(self.api.create_key(master_secret=u"üöä") != None)

        # incorrect types
        def callback():
            self.api.create_key(master_secret=None)
        self.assertRaises(exceptions.InvalidInput, callback)
        def callback():
            self.api.create_key(master_secret=1)
        self.assertRaises(exceptions.InvalidInput, callback)
        def callback():
            self.api.create_key(master_secret=object())
        self.assertRaises(exceptions.InvalidInput, callback)

    def test_standards_compliant(self):
        pass # FIXME check generated against expected output from 3rd parties


if __name__ == '__main__':
    unittest.main()
