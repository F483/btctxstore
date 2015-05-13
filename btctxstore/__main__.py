#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


import apigen
from btctxstore.api import BtcTxStore


if __name__ == "__main__":
    apigen.run(BtcTxStore)

