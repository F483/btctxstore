#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals


from pycoin.tx.Tx import Tx
from pycoin.serialize import b2h, h2b, b2h_rev, h2b_rev
from . import sanitize
from . import control
from . insight import InsightService # XXX rm when added to next pycoin version


class BtcTxStore(): # TODO use apigen when ported to python 3
    """Bitcoin nulldata output io library."""

    def __init__(self, testnet=False, dryrun=False):
        self.testnet = sanitize.flag(testnet)
        self.dryrun = sanitize.flag(dryrun)
        if self.testnet:
            self.service = InsightService("https://test-insight.bitpay.com/")
        else:
            self.service = InsightService("https://insight.bitpay.com/")

    def writebin(self, rawtx, hexdata):
        """Writes <hexdata> as new nulldata output to <rawtx>."""
        tx = sanitize.unsignedtx(rawtx)
        nulldatatxout = sanitize.nulldatatxout(hexdata)
        tx = control.addnulldata(tx, nulldatatxout)
        return tx.as_hex()

    def readbin(self, rawtx):
        """Returns nulldata from <rawtx> as hexdata."""
        tx = sanitize.tx(rawtx)
        data = control.readnulldata(tx)
        return b2h(data)

    def createtx(self, txins, txouts, locktime="0"):
        """Create unsigned rawtx with given txins/txouts as json data.
        <txins>: '[{"txid" : hexdata, "index" : integer}, ...]'
        <txouts>: '[{"address" : hexdata, "value" : satoshis}, ...]'
        """
        locktime = sanitize.positiveinteger(locktime)
        txins = sanitize.txins(txins)
        txouts = sanitize.txouts(self.testnet, txouts)
        tx = Tx(1, txins, txouts, locktime)
        return tx.as_hex()

    def gettx(self, txid):
        """Returns rawtx from <txid>."""
        txid = sanitize.txid(txid)
        tx = self.service.get_tx(txid)
        return tx.as_hex()

    def signtx(self, rawtx, privatekeys):
        """Sign <rawtx> with  given <privatekeys> as json data.
        <privatekeys>: '["privatekey_in_wif_format", ...]'
        """
        tx = sanitize.tx(rawtx)
        secretexponents = sanitize.secretexponents(self.testnet, privatekeys)
        tx = control.signtx(self.service, self.testnet, tx, secretexponents)
        return tx.as_hex()

    def getutxos(self, addresses):
        """Get current utxos for <address>."""
        addresses = sanitize.addresses(addresses)
        spendables = self.service.spendables_for_addresses(addresses)
        def reformat(spendable):
            return {
                "txid" : b2h_rev(spendable.tx_hash),
                "index" : spendable.tx_out_index,
                "value" : spendable.coin_value,
                "script" : b2h(spendable.script)
            }
        return list(map(reformat, spendables))

    def publish(self, rawtx):
        """Publish signed <rawtx> to bitcoin network."""
        tx = sanitize.signedtx(rawtx)
        if not self.dryrun:
            self.service.send_tx(tx)
        return b2h_rev(tx.hash())

    def createkey(self):
        bip32node = control.createkey(self.testnet)
        return bip32node.wif()

    def store(self, hexdata, privatekeys, changeaddress=None, txouts=None,
              fee="10000", locktime="0"):
        """Store <hexdata> in blockchain and return new txid.
        Utxos taken from <privatekeys> and change sent to <changeaddress>.
        <privatekeys>: '["privatekey_in_wif_format", ...]'
        """
        nulldatatxout = sanitize.nulldatatxout(hexdata)
        secretexponents = sanitize.secretexponents(self.testnet, privatekeys)
        txouts = sanitize.txouts(self.testnet, txouts) if txouts else []
        fee = sanitize.positiveinteger(fee)
        locktime = sanitize.positiveinteger(locktime)
        txid = control.store(self.service, self.testnet, nulldatatxout,
                             secretexponents, changeaddress, txouts, fee, 
                             locktime, publish=(not self.dryrun))
        return b2h_rev(txid)

    def retrieve(self, txid):
        """Returns nulldata stored in blockchain <txid> as hexdata."""
        rawtx = self.gettx(txid)
        return self.readbin(rawtx)

