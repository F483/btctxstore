# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from btctxstore.services.insight import Insight
from btctxstore.services.blockexplorer import BlockExplorer


#from btctxstore.services.blockchaininfo import BlockchainInfo
# blockchain.info removed because it doesnt accept transaction with OP_RETURN 


def select(name, testnet=False, dryrun=False):
    service_dict = {  # { "name" : (class, testnet_supported), ... }
        "insight": (Insight, True),
        "blockexplorer": (BlockExplorer, True),
        #"blockchain.info": (BlockchainInfo, False),
    }
    service_class, testnet_supported = service_dict.get(name, (None, False))
    if service_class is None:
        raise Exception("Service {0} not found!".format(name))
    if testnet and not testnet_supported:
        raise Exception("Service {0} does not support testnet!".format(name))
    return service_class(testnet=testnet, dryrun=dryrun)
