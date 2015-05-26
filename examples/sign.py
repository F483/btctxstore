#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)

from __future__ import print_function
from __future__ import unicode_literals

import binascii
from btctxstore import BtcTxStore

data = binascii.hexlify(b"messagetext")
api = BtcTxStore(testnet=True, dryrun=True)
wif = api.createkey() # create new private key
sigsignature = api.signdata(wif, data)
print(signature)
