import json
import logging
import io
from future.moves.urllib.parse import urlencode
from future.moves.urllib.request import urlopen
from future.moves.urllib.error import HTTPError
from pycoin.block import BlockHeader
from pycoin.convention import btc_to_satoshi
from pycoin.encoding import double_sha256
from pycoin.merkle import merkle
from pycoin.serialize import b2h, b2h_rev, h2b, h2b_rev
from pycoin.tx import Spendable, Tx
from btctxstore.services.interface import BlockchainService


_log = logging.getLogger(__name__)


# TODO provide support to insight API servers
# see also https://github.com/bitpay/insight-api


class Insight(BlockchainService):

    def __init__(self, testnet=False, dryrun=False):
        super(Insight, self).__init__(testnet=testnet, dryrun=dryrun)
        if testnet:
            base_url = "https://test-insight.bitpay.com/api"
        else:
            base_url = "https://insight.bitpay.com/api"
        self.base_url = base_url

    def get_blockchain_tip(self):
        url = "%s/status?q=getLastBlockHash" % self.base_url
        d = urlopen(url).read().decode("utf8")
        r = json.loads(d)
        return h2b_rev(r.get("lastblockhash"))

    def get_blockheader(self, block_hash):
        return self.get_blockheader_with_transaction_hashes(block_hash)[0]

    def get_blockheader_with_transaction_hashes(self, block_hash):
        url = "%s/block/%s" % (self.base_url, b2h_rev(block_hash))
        r = json.loads(urlopen(url).read().decode("utf8"))
        version = r.get("version")
        previous_block_hash = h2b_rev(r.get("previousblockhash"))
        merkle_root = h2b_rev(r.get("merkleroot"))
        timestamp = r.get("time")
        difficulty = int(r.get("bits"), 16)
        nonce = int(r.get("nonce"))
        tx_hashes = [h2b_rev(tx_hash) for tx_hash in r.get("tx")]
        blockheader = BlockHeader(version, previous_block_hash, merkle_root,
                                  timestamp, difficulty, nonce)
        if blockheader.hash() != block_hash:
            return None, None
        calculated_hash = merkle(tx_hashes, double_sha256)
        if calculated_hash != merkle_root:
            return None, None
        blockheader.height = r.get("height")
        return blockheader, tx_hashes

    def get_block_height(self, block_hash):
        header = self.get_blockheader_with_transaction_hashes(block_hash)
        return header[0].height

    def get_tx(self, tx_hash):
        url = "%s/rawtx/%s" % (self.base_url, b2h_rev(tx_hash))
        result = json.loads(urlopen(url).read().decode("utf8"))
        tx = Tx.from_hex(result['rawtx'])
        if tx.hash() == tx_hash:
            return tx
        return None

    def confirms(self, txid):
        url = "%s/tx/%s" % (self.base_url, b2h_rev(txid))
        result = json.loads(urlopen(url).read().decode("utf8"))
        return result.get("confirmations", 0)

    def spendables_for_address(self, bitcoin_address):
        url = "{0}/addr/{1}/utxo".format(self.base_url, bitcoin_address)
        result = json.loads(urlopen(url).read().decode("utf8"))
        spendables = []
        for utxo in result:
            value = btc_to_satoshi(str(utxo["amount"]))
            prev_index = utxo["vout"]
            prev_hash = h2b_rev(utxo["txid"])
            script = h2b(utxo["scriptPubKey"])
            spendable = Spendable(value, script, prev_hash, prev_index)
            spendables.append(spendable)
        return spendables

    def send_tx(self, tx):
        if self.dryrun:
            return
        # TODO: make this handle errors better
        s = io.BytesIO()
        tx.stream(s)
        tx_as_hex = b2h(s.getvalue())
        data = urlencode(dict(rawtx=tx_as_hex)).encode("utf8")
        url = "%s/tx/send" % self.base_url
        try:
            return urlopen(url, data=data).read()
        except HTTPError as ex:
            _log.exception("problem in send_tx %s", tx.id())
            raise ex
