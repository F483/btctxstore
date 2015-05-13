##########
btctxstore
##########

A library to read/write data to bitcoin transactions as nulldata outputs.

============
Installation
============

::

  pip install btctxstore


=========
CLI usage
=========

Write data to bitcoin transaction as nulldata new output.
Prints new raw transaction with added output.

::

  python -m btctxstore write_bin <unsigned rawtx hex> <data hex>

Read data from bitcoin transaction with nulldata output.
Prints hex data from output.

::

  python -m btctxstore read_bin <rawtx hex>


============
python usage
============

Write data to bitcoin transaction as nulldata new output.
Prints new raw transaction with added output.

.. code:: python

  from btctxstore import BtcTxStore
  api = BtcTxStore()

  # using hex data
  outputrawtx = api.write_bin(unsignedrawtx, hexdata)

  # using pycoin tx and binary data
  api.write(pycointx, bindata)

Read data from bitcoin transaction with nulldata output.
Prints hex data from output.

.. code:: python

  from btctxstore import BtcTxStore
  api = BtcTxStore()

  # using hex data
  hexdata = api.read_bin(rawtx)

  # using pycoin tx and binary data
  bindata = api.read(pycointx)


==============
json-rpc usage
==============

Starting the rpc server.

::

  python -m btctxstore startserver --hostname=<hostname> --port=<port>

Write data to bitcoin transaction as nulldata new output.
Prints new raw transaction with added output.

.. code:: python

  import pyjsonrpc
  rpc = pyjsonrpc.HttpClient(url = "http://localhost:8080")

  # using hex data
  outputrawtx = rpc.write_bin(unsignedrawtx, hexdata)

Read data from bitcoin transaction with nulldata output.
Prints hex data from output.

.. code:: python

  import pyjsonrpc
  rpc = pyjsonrpc.HttpClient(url = "http://localhost:8080")

  # using hex data
  hexdata = rpc.read_bin(rawtx)



