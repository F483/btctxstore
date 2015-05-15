#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


import re
from pycoin.tx.Tx import Tx
from pycoin.encoding import hash160_sec_to_bitcoin_address
from pycoin.tx.script import tools
from pycoin.serialize import b2h, h2b, b2h_rev, h2b_rev
from pycoin.tx.pay_to import build_hash160_lookup
from pycoin.tx import SIGHASH_ALL 
from pycoin.tx.TxIn import TxIn                                                  


def signtx(service, testnet, tx, secretexponents):
    netcode = 'XTN' if testnet else 'BTC'
    lookup = build_hash160_lookup(secretexponents)
    for txin_idx in xrange(len(tx.txs_in)):
        txin = tx.txs_in[txin_idx]
        utxo_tx = service.get_tx(txin.previous_hash)
        script = utxo_tx.txs_out[txin.previous_index].script
        tx.sign_tx_in(lookup, txin_idx, script, SIGHASH_ALL, netcode=netcode)
    return tx


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


def findtxins(service, addresses, amount):
    spendables = service.spendables_for_addresses(addresses)
    txins = []
    total = 0
    for spendable in spendables:
        utxo_tx = service.get_tx(spendable.tx_hash)
        total += utxo_tx.txs_out[spendable.tx_out_index].coin_value
        txins.append(TxIn(spendable.tx_hash, spendable.tx_out_index))
        if total >= amount:
            return txins, total
    return txins, total


def secretexponents_to_addresses(testnet, secretexponents):
    prefix = b'\x6f' if testnet else b"\0"
    lookup = build_hash160_lookup(secretexponents)
    addresses = []
    for hash160 in lookup.keys():
        address = hash160_sec_to_bitcoin_address(hash160, address_prefix=prefix)
        addresses.append(address)
    return addresses


def store(service, testnet, nulldatatxout, secretexponents, 
          changeout, fee=10000, locktime=0, publish=True):
    
    # txins
    addresses = secretexponents_to_addresses(testnet, secretexponents)
    txins, total = findtxins(service, addresses, fee)
    if total < fee:
        msg = "Insufficient funds! Required: %s Available: %s"
        raise Exception(msg % (amount, total))

    # txouts
    changeout.coin_value = total - fee
    txouts = [nulldatatxout, changeout]

    # create, sign and publish tx
    tx = Tx(1, txins, txouts, locktime)
    tx = signtx(service, testnet, tx, secretexponents)
    if publish:
        service.send_tx(tx)
    return tx.hash()

