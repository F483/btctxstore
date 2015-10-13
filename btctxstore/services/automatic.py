# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)



class Insight(BlockchainService):

    def __init__(self, testnet=False, dryrun=False):
        super(Insight, self).__init__(testnet=testnet, dryrun=dryrun)

    def get_tx(self, txid):
        """TODO doc string"""
        raise NotImplementedError()

    def send_tx(self, tx):
        """TODO doc string"""
        raise NotImplementedError()

    def spendables_for_address(self, bitcoin_address):
        """TODO doc string"""
        raise NotImplementedError()
