#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


import sanitize
import apigen
from pycoin.tx.script import tools
from pycoin.tx.Tx import Tx 
from pycoin.serialize import b2h, h2b
from pycoin.tx.TxOut import TxOut


class BtcTxStore(apigen.Definition):
    """ TODO doc string. """

    def __init__(self, testnet=False):
        self.testnet = testnet

    def write(self, tx, data):
        script_text = "OP_RETURN %s" % b2h(data)
        script_bin = tools.compile(script_text)
        tx.txs_out.append(TxOut(0, script_bin)) 

    @apigen.command()
    def write_bin(self, rawtxhex, datahex):
        """ TODO doc string. """
        tx = Tx.tx_from_hex(rawtxhex)
        data = h2b(datahex)
        if len(data) > 40:
            raise Exception("Data exceeds maximum of 40 bytes!")
        self.write(tx, data)
        # FIXME only allow one nulldata output
        return tx.as_hex()

    @apigen.command()
    def read_bin(self, rawtxhex):
        """ TODO doc string. """

        return "TODO read_bin"


if __name__ == "__main__":                                                                                      
    apigen.run(BtcTxStore)

