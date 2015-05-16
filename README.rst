##########
btctxstore
##########

A library to read/write data to bitcoin transactions as nulldata outputs.

============
Installation
============

::

  pip install btctxstore

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

