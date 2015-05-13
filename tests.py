#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


import unittest
import btctxstore


unsignedrawtx = "0100000001ef5b2eb4b9b0c10449cbabedca45709135d457a04dabd33c1068aaf86562a72b0200000000ffffffff0240420f00000000001976a91491cc9812ca45e7209ff9364ce96527a7c49f1f3188ac3e770400000000001976a9142e330c36e1d0f199fd91446f2210209a0d35caef88ac00000000"


class TestBinary(unittest.TestCase):                                          

    def test_readwrite(self):
        outputtx = btctxstore.write_bin(unsignedrawtx, "f483")
        data = btctxstore.read_bin(outputtx)
        self.assertEquals(data, "f483") 

    def test_only_one_nulldata_output(self):
        def callback():
            outputtx = btctxstore.write_bin(unsignedrawtx, "f483")
            btctxstore.write_bin(outputtx, "f483")
        self.assertRaises(Exception, callback)

    def test_max_data(self):
        max_data = 40 * "aa" # fourty bytes
        btctxstore.write_bin(unsignedrawtx, max_data)
        def callback():
            over_max_data = 41 * "aa" # fourty bytes
            btctxstore.write_bin(unsignedrawtx, over_max_data)
        self.assertRaises(Exception, callback)


if __name__ == '__main__':                                                       
    unittest.main() 


