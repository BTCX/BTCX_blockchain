__author__ = 'sikamedia'
__Date__ = '2014-11-12'


from btcrpc.utils.config_file_reader import  ConfigFileReader
from btcrpc.utils.btc_rpc_call import BTCRPCCall
from btcrpc.utils import log

logger = log.get_log("YAML test")


class AbstractDigitalCurrencyTransfer(object):

    def get_total_amount_in_wallet(self):
        pass

    def transfer_currency(self, from_account='', to_address=''):
        pass


class BTCCurrencyTransfer(AbstractDigitalCurrencyTransfer):

    def __init__(self):

        self.yml_config = ConfigFileReader()
        self.btc_rpc_call = BTCRPCCall(wallet='receive',currency='btc')

    def get_total_amount_in_wallet(self):

        confirms = self.yml_config.get_min_transfer_confirmations(currency='btc')

        lists_of_accounts = self.btc_rpc_call.list_accounts(confirms)
        for account in lists_of_accounts:
            logger.info(account)


if __name__ == "__main__":
    run_transfer = BTCCurrencyTransfer()
    run_transfer.get_total_amount_in_wallet()

