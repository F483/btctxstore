#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)

from __future__ import print_function
from __future__ import unicode_literals
import binascii
from btctxstore import BtcTxStore

api = BtcTxStore(testnet=True, dryrun=True)  # use testing setup for example
wif = api.create_key()  # create new private key
address = api.get_address(wif)  # get private key address
data = binascii.hexlify(b"messagetext")  # hexlify messagetext

# sign data with private key
signature = api.sign_data(wif, data)
print("signature:", signature)

# verify signature (no public or private key needed)
isvalid = api.verify_signature(address, signature, data)
print("valid signature" if isvalid else "invalid signature")
