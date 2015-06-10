# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals
import codecs


def bytestoint(data):
    return int(codecs.encode(data, 'hex_codec'), 16)
