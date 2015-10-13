import io
import json
import logging
import urllib
from urllib.request import urlopen, HTTPError
from urllib.parse import urlencode
from pycoin.serialize import b2h, b2h_rev, h2b
from pycoin.tx import Spendable, Tx
from btctxstore.services.interface import BlockchainService


_log = logging.getLogger(__name__)


class BlockchainInfo(BlockchainService):

    def __init__(self, testnet=False, dryrun=False):
        super(BlockchainInfo, self).__init__(testnet=testnet, dryrun=dryrun)
        if testnet:
            raise NotImplementedError()
        self.base_url = "https://blockchain.info"

    def get_tx(self, tx_hash):
        url = "%s/tx/%s?format=hex" % (self.base_url, b2h_rev(tx_hash))
        raw = urlopen(url).read().decode("utf8")
        tx = Tx.tx_from_hex(raw)
        if tx.hash() == tx_hash:
            return tx
        return None

    def send_tx(self, tx):
        if self.dryrun:
            return
        s = io.BytesIO()
        tx.stream(s)
        tx_as_hex = b2h(s.getvalue())
        data = urlencode(dict(tx=tx_as_hex)).encode("utf8")
        url = "%s/pushtx" % self.base_url
        try:
            d = urlopen(url, data=data).read()
            return d
        except HTTPError as ex:
            d = ex.read()
            _log.error(repr(ex))

    def spendables_for_address(self, bitcoin_address):
        url = "%s/unspent?active=%s&format=json" % (self.base_url, bitcoin_address)
        try:
            result = json.loads(urlopen(url).read().decode("utf8"))
        except ValueError as e:
            # blockchain.info is shit and doesnt return json when no results
            return []
        except urllib.error.HTTPError as e:
            # blockchain.info is shit and fails for an unused address
            if e.code != 500:
                raise e
            return []

        spendables = []
        for u in result["unspent_outputs"]:
            coin_value = u["value"]
            script = h2b(u["script"])
            prev_hash = h2b(u["tx_hash"])
            prev_index = u["tx_output_n"]
            spendable = Spendable(coin_value, script, prev_hash, prev_index)
            spendables.append(spendable)
        return spendables
