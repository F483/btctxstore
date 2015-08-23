# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals


class InvalidInput(Exception):  # FIXME ValueError instead?
    pass


class MaxNulldataExceeded(InvalidInput):

    def __init__(self, bytecount, max_nulldata):
        msg_txt = "Max nulldata exceeded: {0}bytes given, max {1}bytes!"
        msg = msg_txt.format(bytecount, max_nulldata)
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


class InvalidHWIF(InvalidInput):

    def __init__(self, hwif):
        super(InvalidHWIF, self).__init__("Invalid hwif '%s'!" % hwif)


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


class NoDataBlob(Exception):
    
    def __init__(self, tx):
        msg = "No data blob stored in tx '%s'!" % tx.as_hex()
        super(NoDataBlob, self).__init__(msg)


class MaxDataBlobSizeExceeded(Exception):
    
    def __init__(self, max_data_size, data_size):
        msg_txt = "Max data size exceeded! '{0}' given, limit is '{1}' !"
        msg = msg_txt.format(max_data_size, data_size)
        super(MaxDataBlobSizeExceeded, self).__init__(msg)


class NoBroadcastMessage(Exception):
    
    def __init__(self, tx):
        msg = "No broadcast message stored in tx '%s'!" % tx.as_hex()
        super(NoBroadcastMessage, self).__init__(msg)
