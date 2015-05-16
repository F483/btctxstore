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

Store data in bitcoin blockchain in new transaction with nulldata output.
Prints txid of transaction with stored data.

::

  python -m btctxstore store <hexdata> '["pk_in_wif_format", ...]' <change address>

Read data stored in bitcoin blockchain as nulldata output.
Prints stored data in hex format.

::

  python -m btctxstore retrieve <txid>


============
python usage
============

Store data in bitcoin blockchain in new transaction with nulldata output.
Prints txid of transaction with stored data.

.. code:: python

  import json
  from btctxstore import BtcTxStore
  api = BtcTxStore()

  privatekeys = json.dumps([privatekey_in_wif_format])
  txid = api.store(hexdata, privatekeys, changeaddress)
  print txid


Read data stored in bitcoin blockchain as nulldata output.
Prints stored data in hex format.

.. code:: python

  from btctxstore import BtcTxStore
  api = BtcTxStore()

  hexdata = api.retrieve(txid)
  print hexdata



==============
json-rpc usage
==============

Starting the rpc server.

::

  python -m btctxstore startserver --hostname=<hostname> --port=<port>

Store data in bitcoin blockchain in new transaction with nulldata output.
Prints txid of transaction with stored data.

.. code:: python

  import pyjsonrpc
  rpc = pyjsonrpc.HttpClient(url = "http://localhost:8080")

  privatekeys = json.dumps([privatekey_in_wif_format])
  txid = rpc.store(hexdata, privatekeys, changeaddress)
  print txid

Read data stored in bitcoin blockchain as nulldata output.
Prints stored data in hex format.

.. code:: python

  import pyjsonrpc
  rpc = pyjsonrpc.HttpClient(url = "http://localhost:8080")

  hexdata = rpc.retrieve(txid)
  print hexdata



