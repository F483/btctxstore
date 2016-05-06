# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals


import binascii
from btctxstore import serialize
from btctxstore import deserialize
from btctxstore import control
from btctxstore import exceptions
from btctxstore import common
from btctxstore import services
from btctxstore import validate


class BtcTxStore():  # TODO use apigen when ported to python 3
    """Bitcoin nulldata output io library."""

    def __init__(self, testnet=False, dryrun=False, service="automatic"):
        self.testnet = deserialize.flag(testnet)
        self.dryrun = deserialize.flag(dryrun)
        self.service = services.select(service, testnet=testnet,
                                       dryrun=dryrun)

    ###########
    # wallets #
    ###########

    def create_wallet(self, master_secret=b""):
        """Create a BIP0032-style hierarchical wallet.

        @param: master_secret Create from master secret, otherwise random.
        """
        master_secret = deserialize.bytes_str(master_secret)
        bip32node = control.create_wallet(self.testnet,
                                          master_secret=master_secret)
        return bip32node.hwif(as_private=True)

    def validate_wallet(self, hwif):
        return validate.wallet_network(hwif, self.testnet)

    ########
    # keys #
    ########

    def get_key(self, hwif):  # TODO add optional path for sub keys
        bip32node = deserialize.wallet(self.testnet, hwif)
        return bip32node.wif()

    def create_key(self, master_secret=b""):
        """Create new private key and return in wif format.

        @param: master_secret Create from master secret, otherwise random.
        """
        master_secret = deserialize.bytes_str(master_secret)
        bip32node = control.create_wallet(self.testnet,
                                          master_secret=master_secret)
        return bip32node.wif()

    def validate_key(self, wif):  # TODO test
        return validate.key_network(wif, self.testnet)

    #############
    # addresses #
    #############

    def get_address(self, wif):
        """Return bitcoin address for given wallet. """
        return deserialize.key(self.testnet, wif).address()

    def validate_address(self, address):  # TODO test
        return validate.address_network(address, self.testnet)

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

    def send(self, wifs, txouts, change_address=None, lock_time=0, fee=10000):
        """TODO add doc string"""
        # FIXME test!!
        rawtx = self.create_tx(txouts=txouts, lock_time=lock_time)
        rawtx = self.add_inputs(rawtx, wifs, change_address=change_address,
                                fee=fee)
        return self.publish(rawtx)

    def add_inputs(self, rawtx, wifs, change_address=None, fee=10000,
                   dont_sign=False):
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

        if not dont_sign:
            tx = control.sign_tx(self.service, self.testnet, tx, keys)

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

    def sign_unicode(self, wif, message):
        """Signing <unicode> with <wif> private key."""
        hexdata = binascii.hexlify(message.encode("utf-8"))
        return self.sign_data(wif, hexdata)

    def verify_signature_unicode(self, address, signature, message):
        """Verify <signature> of <unicode> by <address>."""
        hexdata = binascii.hexlify(message.encode("utf-8"))
        return self.verify_signature(address, signature, hexdata)

    ###############
    # hash160data #
    ###############

    def add_hash160data(self, rawtx, hexdata, dust_limit=common.DUST_LIMIT):
        """Writes <hexdata> as new Pay-to-PubkeyHash output to <rawtx>."""
        tx = deserialize.unsignedtx(rawtx)
        dust_limit = deserialize.positive_integer(dust_limit)
        hash160data_txout = deserialize.hash160data_txout(hexdata, dust_limit)
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
                          dust_limit=common.DUST_LIMIT):
        """TODO doc string"""
        rawtx = self.create_tx(txouts=txouts, lock_time=lock_time)
        rawtx = self.add_hash160data(rawtx, hexdata, dust_limit=dust_limit)
        rawtx = self.add_inputs(rawtx, wifs, change_address=change_address,
                                fee=fee)
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

    def add_data_blob(self, rawtx, hexdata, dust_limit=common.DUST_LIMIT):
        """TODO add docstring"""
        tx = deserialize.tx(rawtx)
        data = deserialize.binary(hexdata)
        tx = control.add_data_blob(tx, data, dust_limit=dust_limit)
        return serialize.tx(tx)

    def store_data_blob(self, hexdata, wifs, change_address=None,
                        txouts=None, fee=10000, lock_time=0,
                        dust_limit=common.DUST_LIMIT):
        """TODO add docstring"""
        rawtx = self.create_tx(txouts=txouts, lock_time=lock_time)
        rawtx = self.add_data_blob(rawtx, hexdata, dust_limit=dust_limit)
        rawtx = self.add_inputs(rawtx, wifs, change_address=change_address,
                                fee=fee)
        return self.publish(rawtx)

    def retrieve_data_blob(self, txid):
        """TODO add docstring"""
        rawtx = self.retrieve_tx(txid)
        return self.get_data_blob(rawtx)

    #####################
    # broadcast message #
    #####################

    def add_broadcast_message(self, rawtx, message, sender_wif,
                              dust_limit=common.DUST_LIMIT):
        """TODO add docstring"""
        tx = deserialize.tx(rawtx)
        message = deserialize.unicode_str(message)
        sender_key = deserialize.key(self.testnet, sender_wif)
        tx = control.add_broadcast_message(self.testnet, tx, message,
                                           sender_key, dust_limit=dust_limit)
        return serialize.tx(tx)

    def get_broadcast_message(self, rawtx):
        """TODO add docstring"""
        tx = deserialize.tx(rawtx)
        result = control.get_broadcast_message(self.testnet, tx)
        result["signature"] = serialize.signature(result["signature"])
        return result

    def store_broadcast_message(self, message, sender_wif, wifs,
                                change_address=None, txouts=None, fee=10000,
                                lock_time=0, dust_limit=common.DUST_LIMIT):
        """TODO add docstring"""
        rawtx = self.create_tx(txouts=txouts, lock_time=lock_time)
        rawtx = self.add_broadcast_message(rawtx, message, sender_wif,
                                           dust_limit=dust_limit)
        rawtx = self.add_inputs(rawtx, wifs, change_address=change_address,
                                fee=fee)
        return self.publish(rawtx)

    def retrieve_broadcast_message(self, txid):
        """TODO add docstring"""
        rawtx = self.retrieve_tx(txid)
        return self.get_broadcast_message(rawtx)

    ########
    # misc #
    ########

    def confirms(self, txid):
        """Returns number of confirms or None if unpublished."""
        txid = deserialize.txid(txid)
        return self.service.confirms(txid)

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
