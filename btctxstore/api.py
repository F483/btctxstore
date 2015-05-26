#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals


from pycoin.tx.Tx import Tx
from pycoin.serialize import b2h, h2b, b2h_rev, h2b_rev
from . import serialize
from . import deserialize
from . import control
from . insight import InsightService # XXX rm when added to next pycoin version


class BtcTxStore(): # TODO use apigen when ported to python 3
    """Bitcoin nulldata output io library."""

    def __init__(self, testnet=False, dryrun=False):
        self.testnet = deserialize.flag(testnet)
        self.dryrun = deserialize.flag(dryrun)
        if self.testnet:
            self.service = InsightService("https://test-insight.bitpay.com/")
        else:
            self.service = InsightService("https://insight.bitpay.com/")

    # TODO add addaddressdata (encoded as hash160, see cryptograffiti.info)
    # TODO add getaddressdata (encoded as hash160, see cryptograffiti.info)

    def addnulldata(self, rawtx, hexdata):
        """Writes <hexdata> as new nulldata output to <rawtx>."""
        tx = deserialize.unsignedtx(rawtx)
        nulldatatxout = deserialize.nulldatatxout(hexdata)
        return control.addnulldata(tx, nulldatatxout).as_hex()

    def getnulldata(self, rawtx):
        """Returns nulldata from <rawtx> as hexdata."""
        tx = deserialize.tx(rawtx)
        return b2h(control.getnulldata(tx))

    def createkey(self):
        """Create new private key and return in wif format."""
        bip32node = control.createkey(self.testnet)
        return bip32node.wif()

    def createtx(self, txins, txouts, locktime="0"):
        """Create unsigned rawtx with given txins/txouts as json data.
        <txins>: '[{"txid" : hexdata, "index" : integer}, ...]'
        <txouts>: '[{"address" : hexdata, "value" : satoshis}, ...]'
        """
        locktime = deserialize.positiveinteger(locktime)
        txins = deserialize.txins(txins)
        txouts = deserialize.txouts(self.testnet, txouts)
        tx = Tx(1, txins, txouts, locktime)
        return tx.as_hex()

    def signtx(self, rawtx, wifs):
        """Sign <rawtx> with  given <wifs> as json data.
        <wifs>: '["privatekey_in_wif_format", ...]'
        """
        tx = deserialize.tx(rawtx)
        secretexponents = deserialize.secretexponents(self.testnet, wifs)
        tx = control.signtx(self.service, self.testnet, tx, secretexponents)
        return tx.as_hex()

    def retrievetx(self, txid):
        """Returns rawtx for <txid>."""
        txid = deserialize.txid(txid)
        tx = self.service.get_tx(txid)
        return tx.as_hex()

    def retrieveutxos(self, addresses):
        """Get current utxos for <address>."""
        addresses = deserialize.addresses(addresses)
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
        tx = deserialize.signedtx(rawtx)
        if not self.dryrun:
            self.service.send_tx(tx)
        return b2h_rev(tx.hash())

    # TODO add storeaddressdata
    # TODO add retrieveaddressdata

    def storenulldata(self, hexdata, wifs, changeaddress=None, txouts=None,
                      fee="10000", locktime="0"):
        """Store <hexdata> in blockchain and return new txid.
        Utxos taken from <wifs> and change sent to <changeaddress>.
        <wifs>: '["privatekey_in_wif_format", ...]'
        """
        nulldatatxout = deserialize.nulldatatxout(hexdata)
        secretexponents = deserialize.secretexponents(self.testnet, wifs)
        txouts = deserialize.txouts(self.testnet, txouts) if txouts else []
        fee = deserialize.positiveinteger(fee)
        locktime = deserialize.positiveinteger(locktime)
        txid = control.storenulldata(self.service, self.testnet, nulldatatxout,
                                     secretexponents, changeaddress, txouts,
                                     fee, locktime, publish=(not self.dryrun))
        return b2h_rev(txid)

    def retrievenulldata(self, txid):
        """Returns nulldata stored in blockchain <txid> as hexdata."""
        rawtx = self.retrievetx(txid)
        return self.getnulldata(rawtx)

    def getaddress(self, wif):
        """ Return bitcoin address for given wallet. """
        return deserialize.key(wif).address()

    def signdata(self, wif, hexdata):
        """ Signing <hexdata> with <wif> private key."""
        data = deserialize.binary(hexdata)
        key = deserialize.key(wif)
        sig = control.signdata(data, key.secret_exponent())
        for i in range(4):
            sig = serialize.signature(i, False, sig)
            if self.verifysignature(key.address(), sig, hexdata):
                return sig
        raise Exception("Failed to serialize signature!")

    def verifysignature(self, address, signature, hexdata):
        """ Verify <signature> of <hexdata> by <address>."""
        try:
            address = deserialize.address(address)
            data = deserialize.binary(hexdata)
            signature = deserialize.signature(signature)
            return control.verifysignature(self.testnet, address, 
                                           signature, data)
        except Exception as e: # FIXME catch on expected exceptions
            return False




