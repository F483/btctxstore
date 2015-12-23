#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals
import json
import binascii
import unittest
from btctxstore import BtcTxStore
fixtures = json.load(open("tests/fixtures.json"))


class TestVerifySignature(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(dryrun=True, testnet=True)

    def test_verify_positive(self):
        _fixtures = fixtures["verify_signature"]["positive"]
        address = _fixtures["address"]
        signature = _fixtures["signature"]
        data = binascii.hexlify(b"testmessage")
        result = self.api.verify_signature(address, signature, data)
        self.assertEqual(result, True)

    def test_verify_incorrect_address(self):
        _fixtures = fixtures["verify_signature"]["incorrect_address"]
        address = _fixtures["address"]
        signature = _fixtures["signature"]
        data = binascii.hexlify(b"testmessage")
        result = self.api.verify_signature(address, signature, data)
        self.assertEqual(result, False)

    def test_verify_incorrect_signature(self):
        _fixtures = fixtures["verify_signature"]["incorrect_signature"]
        address = _fixtures["address"]
        signature = _fixtures["signature"]
        data = binascii.hexlify(b"testmessage")
        result = self.api.verify_signature(address, signature, data)
        self.assertEqual(result, False)

    def test_verify_incorrect_data(self):
        _fixtures = fixtures["verify_signature"]["incorrect_data"]
        address = _fixtures["address"]
        signature = _fixtures["signature"]
        data = binascii.hexlify(b"testmessagee")
        result = self.api.verify_signature(address, signature, data)
        self.assertEqual(result, False)

    def test_verify_signature_params(self):
        wif = "cSuT2J14dYbe1zvB5z5WTXeRcMbj4tnoKssAK1ZQbnX5HtHfW3bi"
        data = binascii.hexlify(b"testmessage")
        address = self.api.get_address(wif)
        sig = ("/////////////////////////////////////////"
               "//////////////////////////////////////////////=")
        self.assertFalse(self.api.verify_signature(address, sig, data))


if __name__ == '__main__':
    unittest.main()
