#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


import re
from pycoin.tx.script import tools
from pycoin.serialize import b2h, h2b, b2h_rev, h2b_rev


def get_nulldata_txout(tx):
    for out in tx.txs_out:
        if re.match("^OP_RETURN", tools.disassemble(out.script)):
            return out
    return None


def write(tx, nulldatatxout):
    if get_nulldata_txout(tx):
        raise Exception("Transaction already has a nulldata output!")
    # TODO validate transaction is unsigned
    tx.txs_out.append(nulldatatxout)
    # TODO validate transaction
    return tx


def read(tx):
    out = get_nulldata_txout(tx)
    if not out:
        return ""
    return h2b(tools.disassemble(out.script)[10:])


def signtx(service, tx, secretexponents):
    hash160_lookup = build_hash160_lookup(secretexponents)
    for txin_idx in xrange(len(tx.txs_in)):
        previous_hash = tx.txs_in[txin_idx].previous_hash
        previous_index = tx.txs_in[txin_idx].previous_index
        utxo_tx = service.get_tx(previous_hash)
        utxo = utxo_tx.txs_out[index]
        txout_script = h2b(utxo.script)
        tx.sign_tx_in(hash160_lookup, txin_idx, txout_script, SIGHASH_ALL)
    return tx

