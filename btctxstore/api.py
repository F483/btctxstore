#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


import re
import apigen
from pycoin.tx.script import tools
from pycoin.tx.Tx import Tx
from pycoin.serialize import b2h, h2b
from pycoin.tx.TxOut import TxOut


class BtcTxStore(apigen.Definition):
    "btctxstore: read/write data to bitcoin transactions as nulldata outputs."

    def write(self, tx, data):
        if len(data) > 40:
            raise Exception("Data exceeds maximum of 40 bytes!")
        if self._get_nulldata_output(tx):
            raise Exception("Transaction already has a nulldata output!")

        # TODO validate transaction is unsigned

        script_text = "OP_RETURN %s" % b2h(data)
        script_bin = tools.compile(script_text)
        tx.txs_out.append(TxOut(0, script_bin))

        # TODO validate transaction

    def _get_nulldata_output(self, tx):
        for out in tx.txs_out:
            if re.match("^OP_RETURN", tools.disassemble(out.script)):
                return out
        return None

    def read(self, tx):
        out = self._get_nulldata_output(tx)
        if not out:
            return ""
        return h2b(tools.disassemble(out.script)[10:])

    @apigen.command()
    def write_bin(self, rawtxhex, hexdata):
        """Writes <hexdata> as new nulldata output in <rawtxhex>."""
        tx = Tx.tx_from_hex(rawtxhex)
        data = h2b(hexdata)
        self.write(tx, data)
        return tx.as_hex()

    @apigen.command()
    def read_bin(self, rawtxhex):
        """Returns binary nulldata from <rawtxhex> as hexdata."""
        tx = Tx.tx_from_hex(rawtxhex)
        data = self.read(tx)
        return b2h(data)


