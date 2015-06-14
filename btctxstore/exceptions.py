# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals


class InvalidInput(Exception):
    pass


class MaxNulldataExceeded(InvalidInput):

    def __init__(self, bytecount):
        msg = "Max nulldata exceeded: %sbytes given, max 40bytes!" % bytecount
        super(MaxNulldataExceeded, self).__init__(msg)


class InvalidHash160DataSize(InvalidInput):

    def __init__(self, bytecount):
        msg = "Hash160 data != 160bits: %sbits given!" % (bytecount * 8)
        super(InvalidHash160DataSize, self).__init__(msg)


class InvalidAddress(InvalidInput):

    def __init__(self, address):
        super(InvalidAddress, self).__init__("Invalid address '%s'!" % address)


class InvalidWif(InvalidInput):

    def __init__(self, wif):
        super(InvalidWif, self).__init__("Invalid wif '%s'!" % wif)


class InsufficientFunds(Exception):

    def __init__(self, required, available):
        msg = "Insufficient funds! Required: %s Available: %s"
        super(InsufficientFunds, self).__init__(msg % (required, available))


class ExistingNulldataOutput(Exception):

    def __init__(self):
        msg = "Transaction already has a nulldata output!"
        super(ExistingNulldataOutput, self).__init__(msg)


class InvalidSignarureParameter(Exception):

    def __init__(self):
        msg = "Invalid signature parameters!"
        super(InvalidSignarureParameter, self).__init__(msg)


class NoNulldataOutput(Exception):
    
    def __init__(self, tx):
        msg = "No nulldata output for tx '%s'!" % tx.as_hex()
        super(NoNulldataOutput, self).__init__(msg)
