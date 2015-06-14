# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals

import base64
from pycoin.serialize import b2h, b2h_rev


def data(data):
    return b2h(data)


def txid(txhash):
    return b2h_rev(txhash)


def txids(txhashs):
    return list(map(txid, txhashs))


def tx(tx):
    return tx.as_hex()


def signature(sigdata):
    return base64.b64encode(sigdata)


def utxos(spendables):
    def reformat(spendable):
        return {
            "txid": b2h_rev(spendable.tx_hash),
            "index": spendable.tx_out_index,
            "value": spendable.coin_value,
            "script": b2h(spendable.script)
        }
    return list(map(reformat, spendables))
