# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals
import codecs
from pycoin.encoding import from_long
from pycoin.encoding import to_long
from pycoin.encoding import byte_to_int


DUST_LIMIT = 548
MAX_NULLDATA = 40


def bytestoint(data):
    return int(codecs.encode(data, 'hex_codec'), 16)


def chunks(items, size):
    """ Split list into chunks of the given size.
    Original order is preserved.

    Example:
        > chunks([1,2,3,4,5,6,7,8], 3)
        [[1, 2, 3], [4, 5, 6], [7, 8]]
    """
    return [items[i:i+size] for i in range(0, len(items), size)]


def num_to_bytes(bytes_len, v):  # copied from pycoin.encoding.to_bytes_32
    v = from_long(v, 0, 256, lambda x: x)
    if len(v) > bytes_len:
        raise ValueError("input to num_to_bytes is too large")
    return ((b'\0' * bytes_len) + v)[-bytes_len:]


def num_from_bytes(bytes_len, v):  # copied from pycoin.encoding.to_bytes_32
    if len(v) != bytes_len:
        raise ValueError("input to num_from_bytes is wrong length")
    return to_long(256, byte_to_int, v)[0]
