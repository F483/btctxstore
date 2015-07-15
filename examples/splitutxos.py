#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)

from __future__ import print_function
from __future__ import unicode_literals
from btctxstore import BtcTxStore

# Please do not spend the testnet coins is this wallet
# or the example will fail due to lack of funds.
wif = "cUZfG8KJ3BrXneg2LjUX4VoMg76Fcgx6QDiAZj2oGbuw6da8Lzv1"

# use testnet and dont post tx to blockchain for example
api = BtcTxStore(testnet=True, dryrun=True)

limit = 10000000  # 0.1BTC
txids = api.split_utxos(wif, limit)
print(txids)
