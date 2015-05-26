#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)

from __future__ import print_function
from __future__ import unicode_literals

import binascii
from btctxstore import BtcTxStore

address = "mkRqiCnLFFsEH6ezsE1RiMxEjLRXZzWjwe"
signature = "H8wq7z8or7jGGT06ZJ0dC1+wnmRLY/fWnW2SRSRPtypaBAFJAtYhcOl+0jyjujEio91/7eFEW9tuM/WZOusSEGc="
data = binascii.hexlify(b"testmessage")

api = BtcTxStore(testnet=True, dryrun=True)
result = api.verifysignature(address, signature, data)
print(result)

