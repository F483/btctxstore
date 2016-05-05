from btctxstore.services.insight import Insight


class BlockExplorer(Insight):

    def __init__(self, testnet=False, dryrun=False):
        super(BlockExplorer, self).__init__(testnet=testnet, dryrun=dryrun)
        if testnet:
            base_url = "https://testnet.blockexplorer.com/api"
        else:
            base_url = "https://blockexplorer.com/api"
        self.base_url = base_url
