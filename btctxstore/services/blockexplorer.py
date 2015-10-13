import io
import json
import logging
try:
    from urllib2 import HTTPError, urlopen
    from urllib import urlencode
except ImportError:
    from urllib.request import urlopen
    from urllib.error import HTTPError
    from urllib.parse import urlencode
from pycoin.serialize import b2h, b2h_rev, h2b, h2b_rev
from pycoin.tx import Spendable, Tx
from pycoin.convention import btc_to_satoshi
from btctxstore.services.interface import BlockchainService


_log = logging.getLogger(__name__)


class BlockExplorer(BlockchainService):

    def __init__(self, testnet=False, dryrun=False):
        super(BlockExplorer, self).__init__(testnet=testnet, dryrun=dryrun)
        if testnet:
            base_url = "https://testnet.blockexplorer.com/api"
        else:
            base_url = "https://blockexplorer.com/api"
        self.base_url = base_url

    def get_tx(self, tx_hash):
        url = "%s/rawtx/%s" % (self.base_url, b2h_rev(tx_hash))
        result = json.loads(urlopen(url).read().decode("utf8"))
        tx = Tx.tx_from_hex(result["rawtx"])
        if tx.hash() == tx_hash:
            return tx
        return None

    def send_tx(self, tx):
        if self.dryrun:
            return
        s = io.BytesIO()
        tx.stream(s)
        tx_as_hex = b2h(s.getvalue())
        data = urlencode(dict(rawtx=tx_as_hex)).encode("utf8")
        url = "%s/tx/send" % self.base_url
        try:
            d = urlopen(url, data=data).read()
            return d
        except HTTPError as ex:
            d = ex.read()
            _log.error(repr(ex))

    # TODO override spendables_for_addresses
    # api support multiple addresses per query

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
