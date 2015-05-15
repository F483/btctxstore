#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


import sanitize
import apigen
import control
from pycoin.tx.Tx import Tx
from pycoin.serialize import b2h, h2b, b2h_rev, h2b_rev
from insight import InsightService # XXX rm when added to next pycoin version


class BtcTxStore(apigen.Definition):
    """Bitcoin nulldata output io library."""

    def __init__(self, testnet=False, dryrun=False):
        self.testnet = sanitize.flag(testnet)
        self.dryrun = sanitize.flag(dryrun)
        if self.testnet:
            self.service = InsightService("https://test-insight.bitpay.com/")
        else:
            self.service = InsightService("https://insight.bitpay.com/")

    @apigen.command()
    def writebin(self, rawtx, hexdata):
        """Writes <hexdata> as new nulldata output to <rawtx>."""
        tx = sanitize.unsignedtx(rawtx)
        nulldatatxout = sanitize.nulldatatxout(hexdata)
        tx = control.addnulldata(tx, nulldatatxout)
        return tx.as_hex()

    @apigen.command()
    def readbin(self, rawtx):
        """Returns nulldata from <rawtx> as hexdata."""
        tx = sanitize.tx(rawtx)
        data = control.readnulldata(tx)
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
        """TODO doc string"""
        txid = sanitize.txid(txid)
        tx = self.service.get_tx(txid)
        return tx.as_hex()

    @apigen.command()
    def signtx(self, rawtx, privatekeys):
        """Sign <rawtx> with  given <privatekeys> as json data.
        <privatekeys>: '[privatekeywif, ...]'
        """
        tx = sanitize.tx(rawtx)
        secretexponents = sanitize.secretexponents(self.testnet, privatekeys)
        tx = control.signtx(self.service, self.testnet, tx, secretexponents)
        return tx.as_hex()

    @apigen.command()
    def getutxos(self, address):
        """Get current utxos for address."""
        address = sanitize.address(address)
        spendables = self.service.spendables_for_address(address)
        def reformat(spendable):
            return { 
                "txid" : b2h_rev(spendable.tx_hash),
                "index" : spendable.tx_out_index
            }
        return map(reformat, spendables)

    @apigen.command()
    def publish(self, rawtx):
        """Publish signed raw transaction to bitcoin network."""
        tx = sanitize.signedtx(rawtx)
        if not self.dryrun:
            self.service.send_tx(tx) # TODO test it
        return b2h_rev(tx.hash())

    @apigen.command()
    def store(self, hexdata, wifs, changeaddress, fee="10000", locktime="0"):
        """TODO doc string"""
        nulldatatxout = sanitize.nulldatatxout(hexdata)
        secretexponents = sanitize.secretexponents(self.testnet, wifs)
        changeout = sanitize.txout(self.testnet, changeaddress, "0")
        fee = sanitize.positiveinteger(fee)
        locktime = sanitize.positiveinteger(locktime)
        txid = control.store(self.service, self.testnet, nulldatatxout, 
                             secretexponents, changeout, fee, locktime, 
                             publish=(not self.dryrun))
        return b2h_rev(txid)
    
    @apigen.command()
    def retrieve(self, txid): # TODO test it
        """TODO doc string"""
        rawtx = self.gettx(txid)
        return self.readbin(rawtx)

