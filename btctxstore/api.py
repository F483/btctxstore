#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


import re
import sanitize
import apigen
from pycoin.tx.script import tools
from pycoin.tx.Tx import Tx
from pycoin.serialize import b2h, h2b
from pycoin.tx.TxOut import TxOut


class BtcTxStore(apigen.Definition):
    """Bitcoin nulldata output io library."""

    def write(self, tx, nulldataoutput):
        if self._get_nulldata_output(tx):
            raise Exception("Transaction already has a nulldata output!")
        # TODO validate transaction is unsigned
        tx.txs_out.append(nulldataoutput)
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
        tx = sanitize.tx(rawtxhex)
        nulldataoutput = sanitize.nulldataoutput(hexdata)
        self.write(tx, nulldataoutput)
        return tx.as_hex()

    @apigen.command()
    def read_bin(self, rawtxhex):
        """Returns binary nulldata from <rawtxhex> as hexdata."""
        tx = sanitize.tx(rawtxhex)
        data = self.read(tx)
        return b2h(data)

    @apigen.command()
    def new_rawtx(self, txins, txouts, locktime="0", testnet="False"):
        """Create unsigned raw tx with given txins/txouts as json data.
        <txins>: '[{"txid" : hexdata, "index" : number}, ...]'
        <txouts>: '[{"address" : hexdata, "value" : satoshis}, ...]'
        """

        testnet = sanitize.flag(testnet)
        locktime = sanitize.positiveinteger(locktime)
        txins = sanitize.txins(txins)
        txouts = sanitize.txouts(testnet, txouts)
        tx = Tx(1, txins, txouts, locktime)
        return tx.as_hex()

    @apigen.command()
    def sign_rawtx(self, rawtxhex, privatekeys):
        """Sign <rawtxhex> with  given <privatekeys> as json data.
        <privatekeys>: '[privatekeyhex, ...]'
        """
        return "Sorry this feature is not implemented yet."


