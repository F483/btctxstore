# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


import random
import logging
from btctxstore.services.interface import BlockchainService


_log = logging.getLogger(__name__)


class Automatic(BlockchainService):

    def __init__(self, testnet=False, dryrun=False, service_classes=[]):
        super(Automatic, self).__init__(testnet=testnet, dryrun=dryrun)
        if not service_classes:
            raise ValueError()
        self.services = []
        for service_class in service_classes:
            self.services.append(service_class(testnet=testnet, dryrun=dryrun))

    def _select_service(self):
        return random.choice(self.services)

    def _select_other_service(self, service):
        for other_service in self.services:
            if other_service is not service:
                return other_service
        raise Exception("Not enough services!")

    def get_tx(self, txid):
        service = self._select_service()
        try:
            return service.get_tx(txid)
        except Exception as e:
            # try only once with another service
            # if two independant services fail something is wrong
            # there are also only two working services right now ...
            name = service.__class__.__name__
            msg = "Service call to {0} failed: {1}"
            _log.error(msg.format(name, repr(e)))
            other_service = self._select_other_service(service)
            return other_service.get_tx(txid)

    def confirms(self, txid):
        service = self._select_service()
        try:
            return service.confirms(txid)
        except Exception as e:
            # try only once with another service
            # if two independant services fail something is wrong
            # there are also only two working services right now ...
            name = service.__class__.__name__
            msg = "Service call to {0} failed: {1}"
            _log.error(msg.format(name, repr(e)))
            other_service = self._select_other_service(service)
            return other_service.confirms(txid)

    def send_tx(self, tx):
        service = self._select_service()
        try:
            return service.send_tx(tx)
        except Exception as e:
            # try only once with another service
            # if two independant services fail something is wrong
            # there are also only two working services right now ...
            name = service.__class__.__name__
            msg = "Service call to {0} failed: {1}"
            _log.error(msg.format(name, repr(e)))
            other_service = self._select_other_service(service)
            return other_service.send_tx(tx)

    # TODO override spendables_for_addresses in case implementation optimizes

    def spendables_for_address(self, bitcoin_address):
        service = self._select_service()
        try:
            return service.spendables_for_address(bitcoin_address)
        except Exception as e:
            # try only once with another service
            # if two independant services fail something is wrong
            # there are also only two working services right now ...
            name = service.__class__.__name__
            msg = "Service call to {0} failed: {1}"
            _log.error(msg.format(name, repr(e)))
            other_service = self._select_other_service(service)
            return other_service.spendables_for_address(bitcoin_address)
