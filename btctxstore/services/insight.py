import json
import logging
import io
try:
    from urllib2 import HTTPError, urlopen
    from urllib import urlencode
except ImportError:
    from urllib.request import urlopen
    from urllib.error import HTTPError
    from urllib.parse import urlencode
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
            base_url = "https://test-insight.bitpay.com"
        else:
            base_url = "https://insight.bitpay.com"
        self.base_url = base_url

    def get_blockchain_tip(self):
        URL = "%s/api/status?q=getLastBlockHash" % self.base_url
        d = urlopen(URL).read().decode("utf8")
        r = json.loads(d)
        return h2b_rev(r.get("lastblockhash"))

    def get_blockheader(self, block_hash):
        return self.get_blockheader_with_transaction_hashes(block_hash)[0]

    def get_blockheader_with_transaction_hashes(self, block_hash):
        URL = "%s/api/block/%s" % (self.base_url, b2h_rev(block_hash))
        r = json.loads(urlopen(URL).read().decode("utf8"))
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
        URL = "%s/api/rawtx/%s" % (self.base_url, b2h_rev(tx_hash))
        r = json.loads(urlopen(URL).read().decode("utf8"))
        tx = Tx.tx_from_hex(r['rawtx'])
        if tx.hash() == tx_hash:
            return tx
        return None

    def get_tx_confirmation_block(self, tx_hash):
        return self.get_tx(tx_hash).confirmation_block_hash

    def spendables_for_address(self, bitcoin_address):
        URL = "%s/api/addr/%s/utxo" % (self.base_url, bitcoin_address)
        r = json.loads(urlopen(URL).read().decode("utf8"))
        spendables = []
        for u in r:
            value = btc_to_satoshi(str(u.get("amount")))
            script = h2b(u.get("scriptPubKey"))
            prev_hash = h2b_rev(u.get("txid"))
            prev_index = u.get("vout")
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
        URL = "%s/api/tx/send" % self.base_url
        try:
            d = urlopen(URL, data=data).read()
            return d
        except HTTPError as ex:
            _log.exception("problem in send_tx %s", tx.id())
            raise ex
