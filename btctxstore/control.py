#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals


import re
import os
from pycoin.ecdsa import public_pair_for_secret_exponent
from pycoin.ecdsa import generator_secp256k1
from pycoin.tx.Tx import Tx
from pycoin.encoding import hash160_sec_to_bitcoin_address
from pycoin.encoding import public_pair_to_hash160_sec
from pycoin.tx.script import tools
from pycoin.serialize import b2h, h2b, b2h_rev, h2b_rev
from pycoin.tx.pay_to import build_hash160_lookup
from pycoin.tx import SIGHASH_ALL 
from pycoin.tx.TxIn import TxIn                                                  
from pycoin.key.BIP32Node import BIP32Node


from . import sanitize


def getnulldata(tx):
    for out in tx.txs_out:
        if re.match("^OP_RETURN", tools.disassemble(out.script)):
            return out
    return None


def addnulldata(tx, nulldatatxout):
    if getnulldata(tx):
        raise Exception("Transaction already has a nulldata output!")
    # TODO validate transaction is unsigned
    tx.txs_out.append(nulldatatxout)
    # TODO validate transaction
    return tx


def readnulldata(tx):
    out = getnulldata(tx)
    if not out:
        return ""
    return h2b(tools.disassemble(out.script)[10:])


def signtx(service, testnet, tx, secretexponents):
    netcode = 'XTN' if testnet else 'BTC'
    lookup = build_hash160_lookup(secretexponents)
    for txin_idx in range(len(tx.txs_in)):
        txin = tx.txs_in[txin_idx]
        utxo_tx = service.get_tx(txin.previous_hash)
        script = utxo_tx.txs_out[txin.previous_index].script
        tx.sign_tx_in(lookup, txin_idx, script, SIGHASH_ALL, netcode=netcode)
    return tx


def findtxins(service, addresses, amount):
    spendables = service.spendables_for_addresses(addresses)
    txins = []
    total = 0
    for spendable in spendables:
        total += spendable.coin_value
        txins.append(TxIn(spendable.tx_hash, spendable.tx_out_index))
        if total >= amount:
            return txins, total
    return txins, total


def secretexponents_to_addresses(testnet, secretexponents):
    prefix = b'\x6f' if testnet else b"\0"
    addresses = []
    for secretexponents in secretexponents:
        public_pair = public_pair_for_secret_exponent(generator_secp256k1, 
                                                      secretexponents)
        hash160 = public_pair_to_hash160_sec(public_pair, compressed=False)
        address = hash160_sec_to_bitcoin_address(hash160, address_prefix=prefix)
        addresses.append(address)
    return addresses


def store(service, testnet, nulldatatxout, secretexponents, 
          changeaddress=None, txouts=None, fee=10000, 
          locktime=0, publish=True):

    # get required satoshis
    txouts = txouts if txouts else []
    required = sum(list(map(lambda txout: txout.coin_value, txouts))) + fee
    
    # get txins
    addresses = secretexponents_to_addresses(testnet, secretexponents)
    txins, total = findtxins(service, addresses, required)
    if total < required:
        msg = "Insufficient funds! Required: %s Available: %s"
        raise Exception(msg % (required, total))

    # setup txouts
    changeaddress = changeaddress if changeaddress else addresses[0]
    changeout = sanitize.txout(testnet, changeaddress, total - required)
    txouts = txouts + [nulldatatxout, changeout]

    # create, sign and publish tx
    tx = Tx(1, txins, txouts, locktime)
    tx = signtx(service, testnet, tx, secretexponents)
    if publish:
        service.send_tx(tx)
    return tx.hash()


def createkey(testnet):
    netcode = 'XTN' if testnet else 'BTC'
    return BIP32Node.from_master_secret(os.urandom(64), netcode=netcode)


