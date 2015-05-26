# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals


import io
import re
import os
import six
import hashlib
import ecdsa
from pycoin.key import Key
from pycoin.serialize.bitcoin_streamer import stream_bc_int
from pycoin import ecdsa as pycoin_ecdsa # pycoin rolling its own *sigh*
from pycoin.tx.Tx import Tx
from pycoin.encoding import hash160_sec_to_bitcoin_address
from pycoin.encoding import public_pair_to_hash160_sec
from pycoin.encoding import double_sha256
from pycoin.tx.script import tools
from pycoin.serialize import b2h, h2b, b2h_rev, h2b_rev
from pycoin.tx.pay_to import build_hash160_lookup
from pycoin.tx import SIGHASH_ALL
from pycoin.tx.TxIn import TxIn
from pycoin.key.BIP32Node import BIP32Node


from . import util
from . import modsqrt
from . import deserialize


def getnulldataout(tx):
    for out in tx.txs_out:
        if re.match("^OP_RETURN", tools.disassemble(out.script)):
            return out
    return None


def addnulldata(tx, nulldatatxout):
    if getnulldataout(tx):
        raise Exception("Transaction already has a nulldata output!")
    # TODO validate transaction is unsigned
    tx.txs_out.append(nulldatatxout)
    # TODO validate transaction
    return tx


def getnulldata(tx):
    out = getnulldataout(tx)
    if not out:
        return ""
    return h2b(tools.disassemble(out.script)[10:])


def signtx(service, testnet, tx, secretexponents):
    netcode = 'XTN' if testnet else 'BTC'
    lookup = build_hash160_lookup(secretexponents)
    for txin_idx in range(len(tx.txs_in)):
        txin = tx.txs_in[txin_idx]
        utxo_tx = service.get_tx(txin.previous_hash)
        script = utxo_tx.txs_out[txin.previous_index].script
        tx.sign_tx_in(lookup, txin_idx, script, SIGHASH_ALL, netcode=netcode)
    return tx


def findtxins(service, addresses, amount):
    spendables = service.spendables_for_addresses(addresses)
    txins = []
    total = 0
    for spendable in spendables:
        total += spendable.coin_value
        txins.append(TxIn(spendable.tx_hash, spendable.tx_out_index))
        if total >= amount:
            return txins, total
    return txins, total


def public_pair_to_address(testnet, public_pair, compressed):
    prefix = b'\x6f' if testnet else b"\0"
    hash160 = public_pair_to_hash160_sec(public_pair, compressed=compressed)
    return hash160_sec_to_bitcoin_address(hash160, address_prefix=prefix)


def secretexponents_to_addresses(testnet, secretexponents):
    addresses = []
    for secretexponents in secretexponents:
        public_pair = pycoin_ecdsa.public_pair_for_secret_exponent(
            pycoin_ecdsa.generator_secp256k1, secretexponents
        )
        address = public_pair_to_address(testnet, public_pair, False)
        addresses.append(address)
    return addresses


def storenulldata(service, testnet, nulldatatxout, secretexponents,
                  changeaddress=None, txouts=None, fee=10000,
                  locktime=0, publish=True):

    # get required satoshis
    txouts = txouts if txouts else []
    required = sum(list(map(lambda txout: txout.coin_value, txouts))) + fee

    # get txins
    addresses = secretexponents_to_addresses(testnet, secretexponents)
    txins, total = findtxins(service, addresses, required)
    if total < required:
        msg = "Insufficient funds! Required: %s Available: %s"
        raise Exception(msg % (required, total))

    # setup txouts
    changeaddress = changeaddress if changeaddress else addresses[0]
    changeout = deserialize.txout(testnet, changeaddress, total - required)
    txouts = txouts + [nulldatatxout, changeout]

    # create, sign and publish tx
    tx = Tx(1, txins, txouts, locktime)
    tx = signtx(service, testnet, tx, secretexponents)
    if publish:
        service.send_tx(tx)
    return tx.hash()


def createkey(testnet):
    netcode = 'XTN' if testnet else 'BTC'
    return BIP32Node.from_master_secret(os.urandom(64), netcode=netcode)


def encodevarint(value):
    f = io.BytesIO()
    stream_bc_int(f, value)
    return f.getvalue()


def bitcoinmessagehash(data):
    prefix = b"\x18Bitcoin Signed Message:\n"
    varint = encodevarint(len(data))
    return double_sha256(prefix + varint + data)


def signdata(data, secretexponent):
    digest = bitcoinmessagehash(data)
    secp256k1 = ecdsa.curves.SECP256k1
    pk = ecdsa.SigningKey.from_secret_exponent(secretexponent, curve=secp256k1)
    return pk.sign_digest_deterministic(digest, hashfunc=hashlib.sha256,
                                        sigencode=ecdsa.util.sigencode_string)


def recoverpublickey(G, order, r, s, i, e):
    """Recover a public key from a signature.
    See SEC 1: Elliptic Curve Cryptography, section 4.1.6, "Public
    Key Recovery Operation".
    http://www.secg.org/sec1-v2.pdf
    """
    c = ecdsa.ecdsa.curve_secp256k1

    # 1.1 Let x = r + jn 
    x = r + (i // 2) * order

    # 1.3 point from x
    alpha = (x * x * x  + c.a() * x + c.b()) % c.p()
    beta = modsqrt.modular_sqrt(alpha, c.p())
    y = beta if (beta - i) % 2 == 0 else c.p() - beta

    # 1.4 Check that nR is at infinity
    R = ecdsa.ellipticcurve.Point(c, x, y, order)

    rInv = ecdsa.numbertheory.inverse_mod(r, order) # r^-1
    eNeg = -e % order # -e

    # 1.6 compute Q = r^-1 (sR - eG)
    Q = rInv * (s * R + eNeg * G)
    return Q


def parsesignature(sig, order):

    # parse r and s
    rsdata = sig[1:]
    r, s = ecdsa.util.sigdecode_string(rsdata, order)

    # parse parameters
    params = six.indexbytes(sig, 0) - 27
    if params != (params & 7): # At most 3 bits
        raise Exception('Invalid signature parameter!')

    # get compressed parameter
    compressed = bool(params & 4)

    # get recovery parameter
    i = params & 3

    return rsdata, r, s, i, compressed


def verifysignature(testnet, address, sig, data):

    # parse sig data
    G = ecdsa.ecdsa.generator_secp256k1
    order = G.order()
    rsdata, r, s, i, compressed = parsesignature(sig, order)
    digest = bitcoinmessagehash(data)
    e = util.bytestoint(digest)

    # recover public key
    Q = recoverpublickey(G, order, r, s, i, e)
    pub = ecdsa.VerifyingKey.from_public_point(Q, curve=ecdsa.curves.SECP256k1)

    # validate that recovered public key is correct
    sigdecode=ecdsa.util.sigdecode_string
    pub.verify_digest(rsdata, digest, sigdecode=sigdecode)

    # validate that recovered address is correct
    public_pair = [Q.x(), Q.y()]
    recoveredaddress = public_pair_to_address(testnet, public_pair, compressed)
    return address == recoveredaddress


