# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals
import io
import re
import os
import six
import struct
import ecdsa
import math
import zlib
import binascii
import pycoin
from pycoin.key.BIP32Node import BIP32Node
from . import deserialize
from . import serialize
from . import exceptions
from . import common


SIZE_PREFIX_BYTES = 2


# 6 byte data type keys to reduce chance of collision with random data
BROADCAST_MESSAGE_KEY_VERSON_01 = 'b220185f49e7'


def _address_to_hash160(testnet, address):
    prefix = b'\x6f' if testnet else b"\0"
    return pycoin.encoding.bitcoin_address_to_hash160_sec(address,
                                                          address_prefix=prefix)


def _hash160_to_address(testnet, hash160):
    prefix = b'\x6f' if testnet else b"\0"
    return pycoin.encoding.hash160_sec_to_bitcoin_address(hash160,
                                                          address_prefix=prefix)


def add_broadcast_message(testnet, tx, message, sender_key,
                          dust_limit=common.DUST_LIMIT):
    msg_data = message.encode('utf-8')
    signature = sign_data(testnet, msg_data, sender_key)
    hash160 = _address_to_hash160(testnet, sender_key.address())

    # compress after signing in case implementations compress differently
    msg_data = zlib.compress(msg_data, 9)

    data = binascii.unhexlify(BROADCAST_MESSAGE_KEY_VERSON_01)
    data += signature  # 65 byte message signature
    data += 7 * b'\0'  # 7 byte padding so sender hash160 aligns with txout
    data += hash160    # 20 byte aligned sender address (tx in history)
    data += msg_data   # the actual message data

    return add_data_blob(tx, data, dust_limit=dust_limit)


def get_broadcast_message(testnet, tx):

    try:
        data = get_data_blob(tx)
    except exceptions.NoDataBlob:
        raise exceptions.NoBroadcastMessage(tx)

    min_data = 6 + 65 + 7 + 20 + 0  # key + sig + padding + hash160 + message
    if len(data) < min_data:  # not enough data
        raise exceptions.NoBroadcastMessage(tx)

    # parse data
    msg_key = data[:6]  # get key
    data = data[6:]  # remove key
    signature = data[:65]  # get signature
    data = data[65:]  # remove signature
    data = data[7:]  # remove padding
    address = _hash160_to_address(testnet, data[:20])  # get address
    msg_data = data[20:]  # get message data

    if msg_key != binascii.unhexlify(BROADCAST_MESSAGE_KEY_VERSON_01):
        raise exceptions.NoBroadcastMessage(tx)

    # decompress before verification in case
    # implementations compress differently
    try:
        msg_data = zlib.decompress(msg_data)
    except zlib.error:
        raise exceptions.NoBroadcastMessage(tx)

    if not verify_signature(testnet, address, signature, msg_data):
        raise exceptions.NoBroadcastMessage(tx)  # invalid signature

    return {
        "address": address,
        "message": msg_data.decode('utf-8'),
        "signature": signature
    }


def get_data_blob(tx):
    # blob size and initial data stored in nulldata
    try:
        nulldata_index, nulldata = get_nulldata(tx)
    except exceptions.NoNulldataOutput:  # no nulldata output
        raise exceptions.NoDataBlob(tx)

    if len(nulldata) < SIZE_PREFIX_BYTES:  # no data size prefix
        raise exceptions.NoDataBlob(tx)

    # get size and initial data from nulldata
    size = common.num_from_bytes(SIZE_PREFIX_BYTES,
                                 nulldata[:SIZE_PREFIX_BYTES])
    data = nulldata[SIZE_PREFIX_BYTES:]  # strip size prefix

    if size < len(data):  # incorrect size prefix
        raise exceptions.NoDataBlob(tx)

    if size == len(data):  # nulldata was sufficient
        return data

    required_bytes = (size - len(data))
    required_hash160_outputs = int(math.ceil(required_bytes / 20.0))
    if (required_hash160_outputs + nulldata_index + 1) > len(tx.txs_out):
        raise exceptions.NoDataBlob(tx)  # not enough hash160 outputs for data

    for index in range(required_hash160_outputs):
        hash160_index = index + nulldata_index + 1
        data += get_hash160_data(tx, hash160_index)

    return data[:size]  # trim padding of last hash160output


def add_data_blob(tx, data, dust_limit=common.DUST_LIMIT):

    max_data_size = 2 ** (SIZE_PREFIX_BYTES * 8)
    if len(data) > max_data_size:
        raise exceptions.MaxDataBlobSizeExceeded(max_data_size, len(data))

    size_prefix = common.num_to_bytes(SIZE_PREFIX_BYTES, len(data))
    data = size_prefix + data

    # nulldata is sufficient
    if len(data) <= common.MAX_NULLDATA:
        nulldata_txout = deserialize.nulldata_txout(serialize.data(data))
        add_nulldata_output(tx, nulldata_txout)
        return tx

    # prefix and initial data stored in nulldata output
    nulldata = data[:common.MAX_NULLDATA]
    nulldata_txout = deserialize.nulldata_txout(serialize.data(nulldata))
    add_nulldata_output(tx, nulldata_txout)

    # remaining data stored in hash160data outputs
    for hash160data in common.chunks(data[common.MAX_NULLDATA:], 20):
        hexdata = serialize.data(hash160data)
        if len(hexdata) < 40:  # last entry needs padding
            hexdata = hexdata + '0' * (40 - len(hexdata))
        hash160data_txout = deserialize.hash160data_txout(hexdata, dust_limit)
        add_hash160data_output(tx, hash160data_txout)

    return tx


def _get_nulldata_output(tx):
    for index, out in enumerate(tx.txs_out):
        disasm = pycoin.tx.script.tools.disassemble(out.script)
        if re.match("^OP_RETURN", disasm):
            return index, out
    return None, None


def add_nulldata_output(tx, nulldata_txout):
    index, out = _get_nulldata_output(tx)
    if out is not None:
        raise exceptions.ExistingNulldataOutput()
    # TODO validate transaction is unsigned
    tx.txs_out.append(nulldata_txout)
    # TODO validate transaction
    return tx


def add_hash160data_output(tx, hash160data_txout):
    # TODO validate transaction is unsigned
    tx.txs_out.append(hash160data_txout)
    # TODO validate transaction
    return tx


def get_hash160_data(tx, output_index):
    out = tx.txs_out[output_index]
    return pycoin.serialize.h2b(
        pycoin.tx.script.tools.disassemble(out.script)[18:58]
    )


def get_nulldata(tx):
    index, out = _get_nulldata_output(tx)
    if not out:
        raise exceptions.NoNulldataOutput(tx)
    data = pycoin.serialize.h2b(
        pycoin.tx.script.tools.disassemble(out.script)[10:]
    )
    return index, data


def create_tx(service, testnet, txins, txouts,
              lock_time=0, keys=None, publish=False):
    tx = pycoin.tx.Tx(1, txins, txouts, lock_time)
    if keys:
        tx = sign_tx(service, testnet, tx, keys)
    if publish:
        service.send_tx(tx)
    return tx


def sign_tx(service, testnet, tx, keys):
    netcode = 'XTN' if testnet else 'BTC'
    secretexponents = list(map(lambda key: key.secret_exponent(), keys))
    lookup = pycoin.tx.pay_to.build_hash160_lookup(secretexponents)
    for txin_idx in range(len(tx.txs_in)):
        txin = tx.txs_in[txin_idx]
        utxo_tx = service.get_tx(txin.previous_hash)
        script = utxo_tx.txs_out[txin.previous_index].script
        tx.sign_tx_in(lookup, txin_idx, script,
                      pycoin.tx.SIGHASH_ALL, netcode=netcode)
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
        txins.append(pycoin.tx.TxIn(spendable.tx_hash, spendable.tx_out_index))
        if total >= amount:
            return txins, total
    return txins, total


def _public_pair_to_address(testnet, public_pair, compressed):
    hash160 = pycoin.encoding.public_pair_to_hash160_sec(public_pair,
                                                         compressed=compressed)
    return _hash160_to_address(testnet, hash160)


def create_wallet(testnet, master_secret=b""):
    if not master_secret:
        master_secret = os.urandom(256)
    assert(isinstance(master_secret, bytes))
    netcode = 'XTN' if testnet else 'BTC'
    return BIP32Node.from_master_secret(master_secret, netcode=netcode)


def _encode_varint(value):
    f = io.BytesIO()
    pycoin.serialize.bitcoin_streamer.stream_bc_int(f, value)
    return f.getvalue()


def _bitcoin_message_hash(data):
    prefix = b"\x18Bitcoin Signed Message:\n"
    varint = _encode_varint(len(data))
    digest = pycoin.encoding.double_sha256(prefix + varint + data)
    return common.bytestoint(digest)


def _add_recovery_params(i, compressed, sigdata):
    params = 27  # signature parameters
    params += i  # add recovery parameter
    params += 4 if compressed else 0  # add compressed flag
    return struct.pack(b">B", params) + sigdata


def sign_data(testnet, data, key):
    address = key.address()
    e = _bitcoin_message_hash(data)
    secret_exponent = key.secret_exponent()
    G = pycoin.ecdsa.generator_secp256k1

    # sign data
    sig = pycoin.ecdsa.sign(G, secret_exponent, e)
    sigdata = ecdsa.util.sigencode_string(sig[0], sig[1], G.order())

    # add recovery params
    for i in range(4):
        for compressed in [True, False]:
            signature = _add_recovery_params(i, compressed, sigdata)
            if verify_signature(testnet, address, signature, data):
                return signature
    raise Exception("Failed to serialize signature!")


def _recover_public_key(G, order, r, s, i, e):
    """Recover a public key from a signature.
    See SEC 1: Elliptic Curve Cryptography, section 4.1.6, "Public
    Key Recovery Operation".
    http://www.secg.org/sec1-v2.pdf
    """

    c = G.curve()

    # 1.1 Let x = r + jn
    x = r + (i // 2) * order

    # 1.3 point from x
    alpha = (x * x * x + c.a() * x + c.b()) % c.p()
    beta = pycoin.ecdsa.numbertheory.modular_sqrt(alpha, c.p())
    y = beta if (beta - i) % 2 == 0 else c.p() - beta

    # 1.4 Check that nR is at infinity
    R = pycoin.ecdsa.ellipticcurve.Point(c, x, y, order)

    rInv = pycoin.ecdsa.numbertheory.inverse_mod(r, order)  # r^-1
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
        G = pycoin.ecdsa.generator_secp256k1

        # parse sig data
        order = G.order()
        rsdata, r, s, i, compressed = _parse_signature(sig, order)
        e = _bitcoin_message_hash(data)

        # recover public key
        Q = _recover_public_key(G, order, r, s, i, e)
        public_pair = [Q.x(), Q.y()]

        # verify signature
        if not pycoin.ecdsa.verify(G, public_pair, e, [r, s]):
            return False

        # validate that recovered address is correct
        recoveredaddress = _public_pair_to_address(testnet, public_pair,
                                                   compressed)
        return address == recoveredaddress

    except Exception:
        return False


def _take_txins(spendables, limit, max_outputs, fee):
    maxinput = limit * max_outputs + fee
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


def _outputs(testnet, inputs_total, fee, max_outputs, limit, key):
    txouts_total = inputs_total - fee
    if txouts_total > (max_outputs * limit):
        txouts_cnt = max_outputs
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
                fee=10000, max_outputs=100, publish=True):

    spendables = _filter_dust(spendables, fee, limit)
    if not _enough_to_split(spendables, fee, limit):
        return []
    txins, inputs_total = _take_txins(spendables, limit, max_outputs, fee)
    txouts = _outputs(testnet, inputs_total, fee, max_outputs, limit, key)
    tx = create_tx(service, testnet, txins, txouts,
                   keys=[key], publish=publish)

    # recurse for remaining spendables
    return [tx.hash()] + split_utxos(service, testnet, key, spendables, limit,
                                     fee=fee, max_outputs=max_outputs,
                                     publish=publish)


def add_inputs(service, testnet, tx, keys, change_address=None, fee=10000):

    # add inputs
    required = sum([out.coin_value for out in tx.txs_out]) + fee
    addresses = [key.address() for key in keys]
    txins, total = find_txins(service, addresses, required)
    if total < required:
        raise exceptions.InsufficientFunds(required, total)
    tx.txs_in += txins

    # add change output
    change_address = change_address if change_address else addresses[0]
    changeout = deserialize.txout(testnet, change_address, total - required)
    tx.txs_out.append(changeout)

    return tx
