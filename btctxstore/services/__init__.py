# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from btctxstore.services.insight import InsightService


def select(name, testnet=False, dryrun=False):
    service_dict = {  # { "name" : (class, testnet_supported), ... }
        "insight": (InsightService, True),
    }
    service_class, testnet_supported = service_dict.get(name, (None, False))
    if service_class is None:
        raise Exception("Service {0} not found!".format(name))
    if testnet and not testnet_supported:
        raise Exception("Service {0} does not support testnet!".format(name))
    return service_class(testnet=testnet, dryrun=dryrun)
