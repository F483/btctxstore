# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from btctxstore.services.insight import Insight
from btctxstore.services.blockexplorer import BlockExplorer
from btctxstore.services.automatic import Automatic


_all = {
    "insight": Insight,
    "blockexplorer": BlockExplorer,
}


def select(name, testnet=False, dryrun=False):
    service_class = _all.get(name)
    if service_class is not None:
        return service_class(testnet=testnet, dryrun=dryrun)
    if name != "automatic":
        raise Exception("Service {0} not found!".format(name))
    return Automatic(testnet=testnet, dryrun=dryrun,
                     service_classes=_all.values())
