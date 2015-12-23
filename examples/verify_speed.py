#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)

from __future__ import print_function
from __future__ import unicode_literals
from btctxstore import BtcTxStore
import time
import cProfile
from pstats import Stats


api = BtcTxStore(testnet=True, dryrun=True)  # use testing setup for example
wif = api.create_key()  # create new private key
address = api.get_address(wif)  # get private key address
message = "Signed ünicöde message."
signature = api.sign_unicode(wif, message)


profile = cProfile.Profile()
profile.enable()

begin = time.time()
for i in range(10):
    assert(api.verify_signature_unicode(address, signature, message))
end = time.time()

stats = Stats(profile)
stats.strip_dirs()
stats.sort_stats('cumtime')
stats.print_stats()

print(end - begin)
