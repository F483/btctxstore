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


DUST_LIMIT = 548  # FIXME move to common


class BtcTxStore():  # TODO use apigen when ported to python 3
    """Bitcoin nulldata output io library."""

    def __init__(self, testnet=False, dryrun=False):
        self.testnet = deserialize.flag(testnet)
        self.dryrun = deserialize.flag(dryrun)
        if self.testnet:
            self.service = InsightService("https://test-insight.bitpay.com/")
        else:
            self.service = InsightService("https://insight.bitpay.com/")

    #####################
    # wif and addresses #
    #####################

    def create_key(self):
        """Create new private key and return in wif format."""
        bip32node = control.create_key(self.testnet)
        return bip32node.wif()

    def get_address(self, wif):
        """Return bitcoin address for given wallet. """
        return deserialize.key(self.testnet, wif).address()

    ###############
    # transaction #
    ###############

    def create_tx(self, txins=None, txouts=None, lock_time=0):
        """Create unsigned rawtx with given txins/txouts as json data.
        <txins>: '[{"txid" : hexdata, "index" : integer}, ...]'
        <txouts>: '[{"address" : hexdata, "value" : satoshis}, ...]'
        """
        txins = [] if txins is None else txins
        txouts = [] if txouts is None else txouts
        lock_time = deserialize.positive_integer(lock_time)
        txins = deserialize.txins(txins)
        txouts = deserialize.txouts(self.testnet, txouts)
        tx = control.create_tx(self.service, self.testnet, txins, txouts,
                               lock_time=lock_time)
        return serialize.tx(tx)

    def add_inputs(self, rawtx, wifs, change_address=None, fee=10000):
        """Add sufficient inputs from given <wifs> to cover <rawtx> outputs
        and <fee>. If no <change_address> is given, change will be sent to
        first wif.
        """
        tx = deserialize.tx(rawtx)
        keys = deserialize.keys(self.testnet, wifs)
        fee = deserialize.positive_integer(fee)
        if change_address is not None:
            change_address = deserialize.address(self.testnet, change_address)
        tx = control.add_inputs(self.service, self.testnet, tx, keys,
                                change_address=change_address, fee=fee)
        return serialize.tx(tx)

    def sign_tx(self, rawtx, wifs):
        """Sign <rawtx> with  given <wifs> as json data.
        <wifs>: '["privatekey_in_wif_format", ...]'
        """
        tx = deserialize.tx(rawtx)
        keys = deserialize.keys(self.testnet, wifs)
        tx = control.sign_tx(self.service, self.testnet, tx, keys)
        return serialize.tx(tx)

    #################
    # blockchain io #
    #################

    def retrieve_tx(self, txid):
        """Returns rawtx for <txid>."""
        txid = deserialize.txid(txid)
        tx = self.service.get_tx(txid)
        return serialize.tx(tx)

    def retrieve_utxos(self, addresses):
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

    ###########
    # signing #
    ###########

    def sign_data(self, wif, hexdata):
        """Signing <hexdata> with <wif> private key."""
        data = deserialize.binary(hexdata)
        key = deserialize.key(self.testnet, wif)
        sigdata = control.sign_data(self.testnet, data, key)
        return serialize.signature(sigdata)

    def verify_signature(self, address, signature, hexdata):
        """Verify <signature> of <hexdata> by <address>."""
        try:
            address = deserialize.address(self.testnet, address)
            data = deserialize.binary(hexdata)
            signature = deserialize.signature(signature)
            return control.verify_signature(self.testnet, address,
                                            signature, data)
        except exceptions.InvalidAddress:
            return False

    ###############
    # hash160data #
    ###############

    def add_hash160data(self, rawtx, hexdata, value=DUST_LIMIT):
        """Writes <hexdata> as new Pay-to-PubkeyHash output to <rawtx>."""
        tx = deserialize.unsignedtx(rawtx)
        value = deserialize.positive_integer(value)
        hash160data_txout = deserialize.hash160data_txout(hexdata, value)
        tx = control.add_hash160data_output(tx, hash160data_txout)
        return serialize.tx(tx)

    def get_hash160data(self, rawtx, output_index):
        """TODO doc string"""
        tx = deserialize.unsignedtx(rawtx)
        output_index = deserialize.positive_integer(output_index)
        data = control.get_hash160_data(tx, output_index)
        return serialize.data(data)

    def store_hash160data(self, hexdata, wifs, change_address=None,
                          txouts=None, fee=10000, lock_time=0,
                          value=DUST_LIMIT):
        """TODO doc string"""
        rawtx = self.create_tx(txouts=txouts, lock_time=lock_time)
        rawtx = self.add_hash160data(rawtx, hexdata, value=value)
        rawtx = self.add_inputs(rawtx, wifs, change_address=change_address,
                                fee=fee)
        rawtx = self.sign_tx(rawtx, wifs)
        return self.publish(rawtx)

    def retrieve_hash160data(self, txid, output_index):
        """TODO doc string"""
        rawtx = self.retrieve_tx(txid)
        return self.get_hash160_data(rawtx, output_index)

    ############
    # nulldata #
    ############

    def add_nulldata(self, rawtx, hexdata):
        """Writes <hexdata> as new nulldata output to <rawtx>."""
        tx = deserialize.unsignedtx(rawtx)
        nulldata_txout = deserialize.nulldata_txout(hexdata)
        tx = control.add_nulldata_output(tx, nulldata_txout)
        return serialize.tx(tx)

    def get_nulldata(self, rawtx):
        """Returns nulldata from <rawtx> as hexdata."""
        tx = deserialize.tx(rawtx)
        index, data = control.get_nulldata(tx)
        return serialize.data(data)

    def store_nulldata(self, hexdata, wifs, change_address=None, txouts=None,
                       fee=10000, lock_time=0):
        """Store <hexdata> in blockchain and return new txid.
        Utxos taken from <wifs> and change sent to <change_address>.
        <wifs>: '["privatekey_in_wif_format", ...]'
        """
        rawtx = self.create_tx(txouts=txouts, lock_time=lock_time)
        rawtx = self.add_nulldata(rawtx, hexdata)
        rawtx = self.add_inputs(rawtx, wifs, change_address=change_address,
                                fee=fee)
        rawtx = self.sign_tx(rawtx, wifs)
        return self.publish(rawtx)

    def retrieve_nulldata(self, txid):
        """Returns nulldata stored in blockchain <txid> as hexdata."""
        rawtx = self.retrieve_tx(txid)
        return self.get_nulldata(rawtx)

    #############
    # data blob #
    #############

    def get_data_blob(self, rawtx):
        """TODO add docstring"""
        tx = deserialize.tx(rawtx)
        data = control.get_data_blob(tx)
        return serialize.data(data)

    def add_data_blob(self, rawtx, hexdata):
        """TODO add docstring"""
        tx = deserialize.tx(rawtx)
        data = deserialize.binary(hexdata)
        tx = control.add_data_blob(tx, data)
        return serialize.tx(tx)

    def store_data_blob(self, hexdata, wifs, change_address=None, txouts=None,
                        fee=10000, lock_time=0):
        """TODO add docstring"""
        rawtx = self.create_tx(txouts=txouts, lock_time=lock_time)
        rawtx = self.add_data_blob(rawtx, hexdata)
        rawtx = self.add_inputs(rawtx, wifs, change_address=change_address,
                                fee=fee)
        rawtx = self.sign_tx(rawtx, wifs)
        return self.publish(rawtx)

    def retrieve_data_blob(self, txid):
        """TODO add docstring"""
        rawtx = self.retrieve_tx(txid)
        return self.get_data_blob(rawtx)

    #####################
    # broadcast message #
    #####################

    def add_broadcast_message(self, message, sender_wif):
        pass

    def get_broadcast_message(self, rawtx):
        pass

    ########
    # misc #
    ########

    def split_utxos(self, wif, limit, fee=10000, max_outputs=100):
        """Split utxos of <wif> unitil <limit> or <max_outputs> reached."""
        key = deserialize.key(self.testnet, wif)
        limit = deserialize.positive_integer(limit)
        fee = deserialize.positive_integer(fee)
        max_outputs = deserialize.positive_integer(max_outputs)
        spendables = control.retrieve_utxos(self.service, [key.address()])
        txids = control.split_utxos(self.service, self.testnet, key,
                                    spendables, limit, fee=fee,
                                    max_outputs=max_outputs,
                                    publish=(not self.dryrun))
        return serialize.txids(txids)
