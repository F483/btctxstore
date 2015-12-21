# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals
from btctxstore import deserialize
from btctxstore import exceptions


def wallet(hwif, testnet=None):
    if testnet is None:
        return mainnet_wallet(hwif) or testnet_wallet(hwif)
    return wallet_network(hwif, testnet)


def mainnet_wallet(hwif):
    return wallet_network(hwif, False)


def testnet_wallet(hwif):
    return wallet_network(hwif, True)


def wallet_network(hwif, testnet):
    try:
        deserialize.wallet(testnet, hwif)
        return True
    except exceptions.InvalidInput:
        return False


def key(wif, testnet=None):
    if testnet is None:
        return mainnet_key(wif) or testnet_key(wif)
    return key_network(wif, testnet)


def mainnet_key(wif):
    return key_network(wif, False)


def testnet_key(wif):
    return key_network(wif, True)


def key_network(wif, testnet):
    try:
        deserialize.key(testnet, wif)
        return True
    except exceptions.InvalidInput:
        return False


def address(address, testnet=None):
    if testnet is None:
        return mainnet_address(address) or testnet_address(address)
    return address_network(address, testnet)


def mainnet_address(address):
    return address_network(address, False)


def testnet_address(address):
    return address_network(address, True)


def address_network(address, testnet):
    try:
        deserialize.address(testnet, address)
        return True
    except exceptions.InvalidInput:
        return False
