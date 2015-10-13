# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


class BlockchainService(object):

    def __init__(self, testnet=False, dryrun=False):
        """TODO doc string"""
        self.testnet = testnet
        self.dryrun = dryrun

    def get_tx(self, txid):
        """TODO doc string"""
        raise NoImplementedError()
    #tx = self.service.get_tx(txid)

    def send_tx(self, tx):
        """TODO doc string"""
        raise NoImplementedError()
    #self.service.send_tx(tx)

    def spendables_for_addresses(self, addresses):
        """
        Return a list of Spendable objects for the
        given bitcoin address.
        """
        raise NoImplementedError()
    #spendables = service.spendables_for_addresses(addresses)


