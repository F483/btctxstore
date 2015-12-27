##########
btctxstore
##########


|BuildLink|_ |CoverageLink|_ |LicenseLink|_ |IssuesLink|_


.. |BuildLink| image:: https://travis-ci.org/Storj/btctxstore.svg
.. _BuildLink: https://travis-ci.org/Storj/btctxstore

.. |CoverageLink| image:: https://coveralls.io/repos/Storj/btctxstore/badge.svg
.. _CoverageLink: https://coveralls.io/r/Storj/btctxstore

.. |LicenseLink| image:: https://img.shields.io/badge/license-MIT-blue.svg
.. _LicenseLink: https://raw.githubusercontent.com/F483/btctxstore/master/LICENSE

.. |IssuesLink| image:: https://img.shields.io/github/issues/F483/btctxstore.svg
.. _IssuesLink: https://github.com/F483/btctxstore/issues


A library to read/write data to bitcoin transactions as nulldata outputs.


============
Installation
============

Install btctxstore lib

::

  pip install btctxstore


=========================
Use fast native functions
=========================

There is experimental code that will call into OpenSSL for slow functions.
To enable this, set (and export) environment variable PYCOIN_NATIVE=openssl.

::

  $ export PYCOIN_NATIVE=openssl


================================
storing data in nulldata outputs
================================

Store data in blockchain in new transaction with nulldata output.

.. code:: python

  # from examples/store_nulldata.py
  import binascii
  from btctxstore import BtcTxStore

  # Wallet used to pay for fee. Please do not spend the testnet coins is
  # this wallet or the example will fail due to lack of funds.
  wifs = ["cUZfG8KJ3BrXneg2LjUX4VoMg76Fcgx6QDiAZj2oGbuw6da8Lzv1"]

  # use testnet and dont post tx to blockchain for example
  api = BtcTxStore(testnet=True, dryrun=True)

  # store data in blockchain as nulldata output (max 40bytes)
  data = binascii.hexlify(b"github.com/F483/btctxstore")
  txid = api.store_nulldata(data, wifs)
  print(txid)


=====================================
retrieving data from nulldata outputs
=====================================

Retrieve transaction from blockchain and read data stored as nulldata output.

.. code:: python

  # from examples/retrieve_nulldata.py
  from btctxstore import BtcTxStore

  api = BtcTxStore(testnet=True, dryrun=True)  # use testing setup for example
  txid = "987451c344c504d07c1fa12cfbf84b5346535da5154006f6dc8399a8fae127eb"
  hexnulldata = api.retrieve_nulldata(txid)
  print(hexnulldata)


======================================
sign/verify data (bitcoind compatible)
======================================

.. code:: python

  # from examples/signverify.py
  import binascii
  from btctxstore import BtcTxStore

  api = BtcTxStore(testnet=True, dryrun=True)  # use testing setup for example
  wif = api.create_key()  # create new private key
  address = api.get_address(wif)  # get private key address
  data = binascii.hexlify(b"messagetext")  # hexlify messagetext

  # sign data with private key
  signature = api.sign_data(wif, data)
  print("signature:", signature)

  # verify signature (no public or private key needed)
  isvalid = api.verify_signature(address, signature, data)
  print("valid signature" if isvalid else "invalid signature")


===========
Split utxos
===========

Split utxos of wallet unitil limit or max_outputs reached.

.. code:: python

  # from examples/split_utxos.py
  from btctxstore import BtcTxStore

  # Please do not spend the testnet coins is this wallet
  # or the example will fail due to lack of funds.
  wif = "cUZfG8KJ3BrXneg2LjUX4VoMg76Fcgx6QDiAZj2oGbuw6da8Lzv1"

  # use testnet and dont post tx to blockchain for example
  api = BtcTxStore(testnet=True, dryrun=True)

  limit = 10000000  # 0.1BTC
  txids = api.split_utxos(wif, limit)
  print(txids)
