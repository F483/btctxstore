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
from insight import InsightService # XXX rm when added to next pycoin version


class BtcTxStore(apigen.Definition):
    """Bitcoin nulldata output io library."""

    def __init__(self, testnet="False"):
        self.testnet = sanitize.flag(testnet)
        if self.testnet:
            self.service = InsightService("https://test-insight.bitpay.com/")
        else:
            self.service = InsightService("https://insight.bitpay.com/")

    def _get_nulldata_txout(self, tx):
        for out in tx.txs_out:
            if re.match("^OP_RETURN", tools.disassemble(out.script)):
                return out
        return None

    def write(self, tx, nulldatatxout):
        if self._get_nulldata_txout(tx):
            raise Exception("Transaction already has a nulldata output!")
        # TODO validate transaction is unsigned
        tx.txs_out.append(nulldatatxout)
        # TODO validate transaction

    def read(self, tx):
        out = self._get_nulldata_txout(tx)
        if not out:
            return ""
        return h2b(tools.disassemble(out.script)[10:])

    @apigen.command()
    def writebin(self, rawtx, hexdata):
        """Writes <hexdata> as new nulldata output in <rawtx>."""
        tx = sanitize.tx(rawtx)
        nulldatatxout = sanitize.nulldatatxout(hexdata)
        self.write(tx, nulldatatxout)
        return tx.as_hex()

    @apigen.command()
    def readbin(self, rawtx):
        """Returns binary nulldata from <rawtx> as hexdata."""
        tx = sanitize.tx(rawtx)
        data = self.read(tx)
        return b2h(data)

    @apigen.command()
    def createtx(self, txins, txouts, locktime="0"):
        """Create unsigned raw tx with given txins/txouts as json data.
        <txins>: '[{"txid" : hexdata, "index" : number}, ...]'
        <txouts>: '[{"address" : hexdata, "value" : satoshis}, ...]'
        """
        locktime = sanitize.positiveinteger(locktime)
        txins = sanitize.txins(txins)
        txouts = sanitize.txouts(self.testnet, txouts)
        tx = Tx(1, txins, txouts, locktime)
        return tx.as_hex()

    @apigen.command()
    def gettx(self, txid):
        txid = sanitize.txid(txid)
        tx = self.service.get_tx(txid)
        return tx.as_hex()

    @apigen.command()
    def signtx(self, rawtx, privatekeys): # TODO test it
        """Sign <rawtx> with  given <privatekeys> as json data.
        <privatekeys>: '[privatekeyhex, ...]'
        """
        tx = sanitize.tx(rawtx)
        secretexponents = sanitize.secretexponents(privatekeys)
        hash160_lookup = build_hash160_lookup(secretexponents)
        for txin_idx in xrange(len(tx.txs_in)):
            previous_hash = tx.txs_in[txin_idx].previous_hash
            previous_index = tx.txs_in[txin_idx].previous_index
            utxo_tx = self.service.get_tx(previous_hash)
            utxo = utxo_tx.txs_out[index]
            txout_script = h2b(utxo.script)
            tx.sign_tx_in(hash160_lookup, txin_idx, txout_script, SIGHASH_ALL)
        return tx.as_hex()

    @apigen.command()
    def getutxos(self, address):
        """Get current utxos for address."""
        return "Sorry this feature is not implemented yet."

    @apigen.command()
    def publish(self, rawtx):
        """Publish signed raw transaction to bitcoin network."""
        return "Sorry this feature is not implemented yet."

