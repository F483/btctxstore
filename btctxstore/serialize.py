# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals

import struct
import base64
from . import util


def signature(i, compressed, sigdata):
    params = 27 # signature parameters
    params += i # add recovery parameter
    params += 4 if compressed else 0 # add compressed flag
    sig = struct.pack(">B", params) + sigdata
    return base64.b64encode(sig)



