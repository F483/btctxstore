##########
btctxstore
##########

A library to read/write data to bitcoin transactions as nulldata outputs.

============
Installation
============

::

  pip install btctxstore

=============================================
storing/retrieving data from nulldata outputs
=============================================

Store data in bitcoin blockchain in new transaction with nulldata output.
Prints txid of transaction with stored data.

.. code:: python

  from btctxstore import BtcTxStore
  api = BtcTxStore()

  privatekeys = [privatekey_in_wif_format]
  txid = api.storenulldata(hexnulldata, privatekeys)
  print(txid)


Read data stored in bitcoin blockchain as nulldata output.
Prints stored data in hex format.

.. code:: python

  from btctxstore import BtcTxStore
  api = BtcTxStore()

  hexnulldata = api.retrievenulldata(txid)
  print(hexnulldata)

======================================
sign/verify data (bitcoind compatible)
======================================

Signing message with a private key.

.. code:: python

  # from examples/sign.py
  import binascii
  from btctxstore import BtcTxStore

  data = binascii.hexlify(b"messagetext")
  api = BtcTxStore(testnet=True, dryrun=True)
  wif = api.createkey() # create new private key
  sigsignature = api.signdata(wif, data)
  print(signature)

Verify signature with address, signature and data.

.. code:: python

  # from examples/verify.py
  import binascii
  from btctxstore import BtcTxStore

  address = "mkRqiCnLFFsEH6ezsE1RiMxEjLRXZzWjwe"
  signature = "H8wq7z8or7jGGT06ZJ0dC1+wnmRLY/fWnW2SRSRPtypaBAFJAtYhcOl+0jyjujEio91/7eFEW9tuM/WZOusSEGc="
  data = binascii.hexlify(b"testmessage")

  api = BtcTxStore(testnet=True, dryrun=True)
  result = api.verifysignature(address, signature, data)
  print(result)

