#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals
from . import serialize
from . import deserialize
from . import control
from . import exceptions
from . insight import InsightService  # XXX rm when added to pycoin


class BtcTxStore():  # TODO use apigen when ported to python 3
    """Bitcoin nulldata output io library."""

    def __init__(self, testnet=False, dryrun=False):
        self.testnet = deserialize.flag(testnet)
        self.dryrun = deserialize.flag(dryrun)
        if self.testnet:
            self.service = InsightService("https://test-insight.bitpay.com/")
        else:
            self.service = InsightService("https://insight.bitpay.com/")

    def addhash160data(self, rawtx, hexdata, value=548):
        """Writes <hexdata> as new Pay-to-PubkeyHash output to <rawtx>."""
        tx = deserialize.unsignedtx(rawtx)
        value = deserialize.positive_integer(value)
        hash160data_txout = deserialize.hash160data_txout(hexdata, value)
        tx = control.add_hash160data_output(tx, hash160data_txout)
        return serialize.tx(tx)

    def gethash160data(self, rawtx, output_index):
        tx = deserialize.unsignedtx(rawtx)
        output_index = deserialize.positive_integer(output_index)
        data = control.get_hash160_data(tx, output_index)
        return serialize.data(data)

    def addnulldata(self, rawtx, hexdata):
        """Writes <hexdata> as new nulldata output to <rawtx>."""
        tx = deserialize.unsignedtx(rawtx)
        nulldata_txout = deserialize.nulldata_txout(hexdata)
        tx = control.add_nulldata_output(tx, nulldata_txout)
        return serialize.tx(tx)

    def getnulldata(self, rawtx):
        """Returns nulldata from <rawtx> as hexdata."""
        tx = deserialize.tx(rawtx)
        data = control.get_nulldata(tx)
        return serialize.data(data)

    def createkey(self):
        """Create new private key and return in wif format."""
        bip32node = control.create_key(self.testnet)
        return bip32node.wif()

    def createtx(self, txins, txouts, locktime="0"):
        """Create unsigned rawtx with given txins/txouts as json data.
        <txins>: '[{"txid" : hexdata, "index" : integer}, ...]'
        <txouts>: '[{"address" : hexdata, "value" : satoshis}, ...]'
        """
        locktime = deserialize.positive_integer(locktime)
        txins = deserialize.txins(txins)
        txouts = deserialize.txouts(self.testnet, txouts)
        tx = control.create_tx(self.service, self.testnet, txins, txouts,
                               locktime=locktime)
        return serialize.tx(tx)

    def signtx(self, rawtx, wifs):
        """Sign <rawtx> with  given <wifs> as json data.
        <wifs>: '["privatekey_in_wif_format", ...]'
        """
        tx = deserialize.tx(rawtx)
        keys = deserialize.keys(self.testnet, wifs)
        tx = control.sign_tx(self.service, self.testnet, tx, keys)
        return serialize.tx(tx)

    def retrievetx(self, txid):
        """Returns rawtx for <txid>."""
        txid = deserialize.txid(txid)
        tx = self.service.get_tx(txid)
        return serialize.tx(tx)

    def retrieveutxos(self, addresses):
        """Get current utxos for <address>."""
        addresses = deserialize.addresses(self.testnet, addresses)
        spendables = control.retrieve_utxos(self.service, addresses)
        return serialize.utxos(spendables)

    def publish(self, rawtx):
        """Publish signed <rawtx> to bitcoin network."""
        tx = deserialize.signedtx(rawtx)
        if not self.dryrun:
            self.service.send_tx(tx)
        return serialize.txid(tx.hash())

    def storenulldata(self, hexdata, wifs, changeaddress=None, txouts=None,
                      fee="10000", locktime="0"):
        """Store <hexdata> in blockchain and return new txid.
        Utxos taken from <wifs> and change sent to <changeaddress>.
        <wifs>: '["privatekey_in_wif_format", ...]'
        """
        nulldata_txout = deserialize.nulldata_txout(hexdata)
        keys = deserialize.keys(self.testnet, wifs)
        txouts = deserialize.txouts(self.testnet, txouts) if txouts else []
        fee = deserialize.positive_integer(fee)
        locktime = deserialize.positive_integer(locktime)
        txid = control.store_nulldata(self.service, self.testnet,
                                      nulldata_txout, keys, changeaddress,
                                      txouts, fee, locktime,
                                      publish=(not self.dryrun))
        return serialize.txid(txid)

    def retrievenulldata(self, txid):
        """Returns nulldata stored in blockchain <txid> as hexdata."""
        rawtx = self.retrievetx(txid)
        return self.getnulldata(rawtx)

    def getaddress(self, wif):
        """Return bitcoin address for given wallet. """
        return deserialize.key(self.testnet, wif).address()

    def signdata(self, wif, hexdata):
        """Signing <hexdata> with <wif> private key."""
        data = deserialize.binary(hexdata)
        key = deserialize.key(self.testnet, wif)
        sigdata = control.sign_data(self.testnet, data, key)
        return serialize.signature(sigdata)

    def verifysignature(self, address, signature, hexdata):
        """Verify <signature> of <hexdata> by <address>."""
        try:
            address = deserialize.address(self.testnet, address)
            data = deserialize.binary(hexdata)
            signature = deserialize.signature(signature)
            return control.verify_signature(self.testnet, address,
                                            signature, data)
        except exceptions.InvalidAddress:
            return False

    def splitutxos(self, wif, limit, fee=10000, maxoutputs=100):
        """Split utxos of <wif> unitil <limit> or <maxoutputs> reached."""
        key = deserialize.key(self.testnet, wif)
        limit = deserialize.positive_integer(limit)
        fee = deserialize.positive_integer(fee)
        maxoutputs = deserialize.positive_integer(maxoutputs)
        spendables = control.retrieve_utxos(self.service, [key.address()])
        txids = control.split_utxos(self.service, self.testnet, key, spendables,
                                    limit, fee=fee, maxoutputs=maxoutputs,
                                    publish=(not self.dryrun))
        return serialize.txids(txids)
