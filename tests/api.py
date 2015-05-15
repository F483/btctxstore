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

    def test_max_data(self): # TODO move to sanitize tests
        max_data = 40 * "aa" # fourty bytes
        self.api.writebin(unsignedrawtx, max_data)
        def callback():
            over_max_data = 41 * "aa" # fourty bytes
            self.api.writebin(unsignedrawtx, over_max_data)
        self.assertRaises(Exception, callback)


class TestCreateTx(unittest.TestCase):

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


class TestGetTx(unittest.TestCase):

    def setUp(self):
        self.api = BtcTxStore(testnet=True)

    def test_get(self):
        txid = "6771c240340d58ff94f186fd5c332edaacf78287a707548bb4fa118446a2b6e6"
        expected = "0100000005fbe5e8f3e73ef35223693dbd0fb30bf736dc2845eaf9f19298553499ccc5b8ab000000006a47304402200249fb2acce22cd0aa6169af363a8f0d47b7f2ebe7cc13721bfda971cd6580e002206299aa96c623e87e786f7439e67538cd162bc66aea82f9ed8486ea2baefc5dd60121023b7a920adaa336636dbb7695f4a54a41cabe115a02da15968b60ca3f0f259abdfffffffffa298e13ab98b5a05e38309a1c9cc2c3c3c5917833766f7dd47d30097b72ef2a000000006b483045022100bfc5d9326f9f087d848d6e147813bee58e930e3651626facef4205a42c6b5c5002200531d0b4459151ca211e7e7d0fa934b0bb8d9aceed620df8402198f56a35c62501210336e3be12e8f3af99ea558ad38c6a74f734ffe4ab637260edc9074a3315f4b61fffffffffb854eeac74c0b49fb51c4796d399ad6aece93ecfded276abd3b3e2828b2dc53a000000006a47304402205a1ced715ec54a2d8de500967d7417687991aaca98de8fabe49074127ce5de1602205552d11b98e57a4d610942daf2219e7418ee00b0bb333edf5fbf8d100214073301210336e3be12e8f3af99ea558ad38c6a74f734ffe4ab637260edc9074a3315f4b61fffffffff9a77d1b1cc5a4de2fe1430d4f9eba979ddb57458936895a2f5a9c3ab66932d0c000000006b483045022100f248bcf00ac51ba379fdc54b0e416c3edc25a1384486c19ffb936b43d15251a002205bfa83197cedbb8d57bbbd24ca481225c6580d81ebb55c10fffe28c2f25e6fcb01210336e3be12e8f3af99ea558ad38c6a74f734ffe4ab637260edc9074a3315f4b61fffffffff7eed8aa0967b3b3c2e356e42625d08f19800340167ee44ce6bb914899a6318c2010000006b4830450221009518c85d81d406f79f328858d6f54ed6f2513ffa8402e1d760a3310546ae618602203e9cb55c358f5d1a47d66ac00b441ae7886b875070c96742882e1048dae42fb7012102e9b7c0513cd82c91ea07c6e9de8ad09509fd098a96c761d25d4d1add010a7c16ffffffff0360e31600000000001976a914ebaa4d22f4e3f8394d5c27affe45be744cd87d1788ace8e64900000000001976a9144cd52ad04a3b90ad6e73ac0ad13e2da1c81c930b88ac0000000000000000676a4c647b226c6162656c223a227b5c226e616d655c223a5c22e5bdb1e9948b5c222c5c22656d61696c5c223a5c227265626f726e31313238403136332e636f6d5c222c5c22746f5f656d61696c5c223a5c225c227d222c226d657373616765223a22313233227d00000000"
        result = self.api.gettx(txid)
        self.assertEquals(result, expected)


if __name__ == '__main__':
    unittest.main()


