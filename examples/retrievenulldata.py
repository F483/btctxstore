#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)

from __future__ import print_function
from __future__ import unicode_literals
from btctxstore import BtcTxStore

api = BtcTxStore(testnet=True, dryrun=True)  # use testing setup for example
txid = "987451c344c504d07c1fa12cfbf84b5346535da5154006f6dc8399a8fae127eb"
hexnulldata = api.retrieve_nulldata(txid)
print(hexnulldata)
