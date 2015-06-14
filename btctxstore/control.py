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
import struct
import ecdsa
from ecdsa.curves import SECP256k1
from pycoin.serialize.bitcoin_streamer import stream_bc_int
from pycoin.tx.Tx import Tx
from pycoin.encoding import hash160_sec_to_bitcoin_address
from pycoin.encoding import public_pair_to_hash160_sec
from pycoin.encoding import double_sha256
from pycoin.tx.script import tools
from pycoin.serialize import h2b
from pycoin.tx.pay_to import build_hash160_lookup
from pycoin.tx import SIGHASH_ALL
from pycoin.tx.TxIn import TxIn
from pycoin.key.BIP32Node import BIP32Node
from . import util
from . import modsqrt
from . import deserialize
from . import serialize
from . import exceptions


def get_nulldata_output(tx):
    for out in tx.txs_out:
        if re.match("^OP_RETURN", tools.disassemble(out.script)):
            return out
    return None


def add_nulldata_output(tx, nulldatatxout):
    if get_nulldata_output(tx):
        raise exceptions.ExistingNulldataOutput()
    # TODO validate transaction is unsigned
    tx.txs_out.append(nulldatatxout)
    # TODO validate transaction
    return tx


def add_hash160data_output(tx, hash160data_txout):
    # TODO validate transaction is unsigned
    tx.txs_out.append(hash160data_txout)
    # TODO validate transaction
    return tx


def get_hash160_data(tx, output_index):
    out = tx.txs_out[output_index]
    return h2b(tools.disassemble(out.script)[18:58])


def get_nulldata(tx):
    out = get_nulldata_output(tx)
    if not out:
        raise exceptions.NoNulldataOutput(tx)
    return h2b(tools.disassemble(out.script)[10:])


def create_tx(service, testnet, txins, txouts,
              locktime=0, keys=None, publish=False):
    tx = Tx(1, txins, txouts, locktime)
    if keys:
        tx = sign_tx(service, testnet, tx, keys)
    if publish:
        service.send_tx(tx)
    return tx


def sign_tx(service, testnet, tx, keys):
    netcode = 'XTN' if testnet else 'BTC'
    secretexponents = list(map(lambda key: key.secret_exponent(), keys))
    lookup = build_hash160_lookup(secretexponents)
    for txin_idx in range(len(tx.txs_in)):
        txin = tx.txs_in[txin_idx]
        utxo_tx = service.get_tx(txin.previous_hash)
        script = utxo_tx.txs_out[txin.previous_index].script
        tx.sign_tx_in(lookup, txin_idx, script, SIGHASH_ALL, netcode=netcode)
    return tx


def retrieve_utxos(service, addresses):
    spendables = service.spendables_for_addresses(addresses)
    spendables = sorted(spendables, key=lambda s: s.coin_value, reverse=True)
    return spendables


def find_txins(service, addresses, amount):
    spendables = retrieve_utxos(service, addresses)
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


def store_nulldata(service, testnet, nulldatatxout, keys,
                   changeaddress=None, txouts=None, fee=10000,
                   locktime=0, publish=True):

    # get required satoshis
    txouts = txouts if txouts else []
    required = sum(list(map(lambda txout: txout.coin_value, txouts))) + fee

    # get txins
    addresses = list(map(lambda key: key.address(), keys))
    txins, total = find_txins(service, addresses, required)
    if total < required:
        raise exceptions.InsufficientFunds(required, total)

    # setup txouts
    changeaddress = changeaddress if changeaddress else addresses[0]
    changeout = deserialize.txout(testnet, changeaddress, total - required)
    txouts = txouts + [nulldatatxout, changeout]

    # create, sign and publish tx
    tx = Tx(1, txins, txouts, locktime)
    tx = sign_tx(service, testnet, tx, keys)
    if publish:
        service.send_tx(tx)
    return tx.hash()


def create_key(testnet):
    netcode = 'XTN' if testnet else 'BTC'
    return BIP32Node.from_master_secret(os.urandom(64), netcode=netcode)


def _encode_varint(value):
    f = io.BytesIO()
    stream_bc_int(f, value)
    return f.getvalue()


def _bitcoin_message_hash(data):
    prefix = b"\x18Bitcoin Signed Message:\n"
    varint = _encode_varint(len(data))
    return double_sha256(prefix + varint + data)


def _add_recovery_params(i, compressed, sigdata):
    params = 27  # signature parameters
    params += i  # add recovery parameter
    params += 4 if compressed else 0  # add compressed flag
    return struct.pack(">B", params) + sigdata


def sign_data(testnet, data, key):
    address = key.address()
    digest = _bitcoin_message_hash(data)
    secretexponent = key.secret_exponent()
    sigencode = ecdsa.util.sigencode_string

    # sign data
    pk = ecdsa.SigningKey.from_secret_exponent(secretexponent, curve=SECP256k1)
    sigdata = pk.sign_digest_deterministic(digest, hashfunc=hashlib.sha256,
                                           sigencode=sigencode)

    # add recovery params
    for i in range(4):
        for compressed in [True, False]:
            sig = _add_recovery_params(i, compressed, sigdata)
            if verify_signature(testnet, address, sig, data):
                return sig
    raise Exception("Failed to serialize signature!")


def _recover_public_key(G, order, r, s, i, e):
    """Recover a public key from a signature.
    See SEC 1: Elliptic Curve Cryptography, section 4.1.6, "Public
    Key Recovery Operation".
    http://www.secg.org/sec1-v2.pdf
    """
    c = ecdsa.ecdsa.curve_secp256k1

    # 1.1 Let x = r + jn
    x = r + (i // 2) * order

    # 1.3 point from x
    alpha = (x * x * x + c.a() * x + c.b()) % c.p()
    beta = modsqrt.modular_sqrt(alpha, c.p())
    y = beta if (beta - i) % 2 == 0 else c.p() - beta

    # 1.4 Check that nR is at infinity
    R = ecdsa.ellipticcurve.Point(c, x, y, order)

    rInv = ecdsa.numbertheory.inverse_mod(r, order)  # r^-1
    eNeg = -e % order  # -e

    # 1.6 compute Q = r^-1 (sR - eG)
    Q = rInv * (s * R + eNeg * G)
    return Q


def _parse_signature(sig, order):

    # parse r and s
    rsdata = sig[1:]
    r, s = ecdsa.util.sigdecode_string(rsdata, order)

    # parse parameters
    params = six.indexbytes(sig, 0) - 27
    if params != (params & 7):  # At most 3 bits
        raise exceptions.InvalidSignarureParameter()

    # get compressed parameter
    compressed = bool(params & 4)

    # get recovery parameter
    i = params & 3

    return rsdata, r, s, i, compressed


def verify_signature(testnet, address, sig, data):

    try:
        # parse sig data
        G = ecdsa.ecdsa.generator_secp256k1
        order = G.order()
        rsdata, r, s, i, compressed = _parse_signature(sig, order)
        digest = _bitcoin_message_hash(data)
        e = util.bytestoint(digest)

        # recover public key
        Q = _recover_public_key(G, order, r, s, i, e)
        pub = ecdsa.VerifyingKey.from_public_point(Q, curve=SECP256k1)

        # validate that recovered public key is correct
        sigdecode = ecdsa.util.sigdecode_string
        pub.verify_digest(rsdata, digest, sigdecode=sigdecode)

        # validate that recovered address is correct
        public_pair = [Q.x(), Q.y()]
        recoveredaddress = public_pair_to_address(testnet, public_pair,
                                                  compressed)
        return address == recoveredaddress

    except AssertionError:  # _recover_public_key failed
        return False
    except exceptions.InvalidSignarureParameter:
        return False


def _take_txins(spendables, limit, maxoutputs, fee):
    maxinput = limit * maxoutputs + fee
    inputs = []
    while True:
        inputs_total = sum(list(map(lambda s: s.coin_value, inputs)))
        if inputs_total > maxinput or not spendables:
            break
        inputs.append(spendables.pop())
    txins = deserialize.txins(serialize.utxos(inputs))
    return txins, inputs_total


def _enough_to_split(spendables, fee, limit):
    total = sum(list(map(lambda s: s.coin_value, spendables)))
    return total >= (fee + limit * 2)


def _filter_dust(spendables, fee, limit):
    spendables = filter(lambda s: s.coin_value > fee, spendables)
    spendables = filter(lambda s: s.coin_value > limit, spendables)
    spendables = sorted(spendables, key=lambda s: s.coin_value)
    return spendables


def _outputs(testnet, inputs_total, fee, maxoutputs, limit, key):
    txouts_total = inputs_total - fee
    if txouts_total > (maxoutputs * limit):
        txouts_cnt = maxoutputs
    else:
        txouts_cnt = txouts_total // limit
    txout_amount = txouts_total // txouts_cnt
    rounded_amount = (txouts_total - txout_amount * txouts_cnt)
    txouts = []
    for i in range(txouts_cnt):
        value = txout_amount + rounded_amount if i == 0 else txout_amount
        txouts.append(deserialize.txout(testnet, key.address(), value))
    assert(txouts_total == sum(list(map(lambda o: o.coin_value, txouts))))
    return txouts


def split_utxos(service, testnet, key, spendables, limit,
                fee=10000, maxoutputs=100, publish=True):

    spendables = _filter_dust(spendables, fee, limit)
    if not _enough_to_split(spendables, fee, limit):
        return []
    txins, inputs_total = _take_txins(spendables, limit, maxoutputs, fee)
    txouts = _outputs(testnet, inputs_total, fee, maxoutputs, limit, key)
    tx = create_tx(service, testnet, txins, txouts,
                   keys=[key], publish=publish)

    # recurse for remaining spendables
    return [tx.hash()] + split_utxos(service, testnet, key, spendables, limit,
                                     fee=fee, maxoutputs=maxoutputs,
                                     publish=publish)
