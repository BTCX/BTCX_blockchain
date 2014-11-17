__author__ = 'sikamedia'
__Date__ = '2014-11-12'


from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.btc_rpc_call import BTCRPCCall
from btcrpc.utils import log


logger_file = log.get_file_logger("Transfer bitcoins", "run_transfer.log")


class AbstractDigitalCurrencyTransfer(object):

    def get_total_amount_in_wallet(self):
        pass

    def transfer_currency(self, from_account='', to_address=''):
        pass


class BTCCurrencyTransfer(AbstractDigitalCurrencyTransfer):

    def __init__(self):

        self.yml_config = ConfigFileReader()
        self.btc_rpc_call = BTCRPCCall(wallet='receive', currency='btc')
        self.coin_to_be_send_dict = self.__init_dict_of_accounts()

    def __get_total_amount_in_wallet(self):

        return reduce(lambda (coin_value), y: coin_value + y, self.coin_to_be_send_dict.values())

    def __init_dict_of_accounts(self):

        confirms = self.yml_config.get_min_transfer_confirmations(currency='btc')
        lists_received_by_account = self.btc_rpc_call.list_accounts(confirms)

        dict_coin_to_be_send = {}

        for received_account, amount in lists_received_by_account.iteritems():

            amount_balance = self.btc_rpc_call.get_balance(received_account, confirms)

            if amount_balance > 0:
                dict_coin_to_be_send[received_account] = amount_balance

        return dict_coin_to_be_send

    def __create_an_address_with_account_assigned(self):

        new_address = self.btc_rpc_call.do_get_new_address()
        self.btc_rpc_call.do_set_account(new_address, new_address)
        return new_address

    def main(self):

        min_transfer = self.yml_config.get_min_transfer_amount(currency='btc')

        total_amount = self.__get_total_amount_in_wallet()

        logger_file.info(total_amount)
        balance_amount = (self.btc_rpc_call.do_getinfo())['balance']

        amount_thresh = abs(balance_amount - total_amount)

        if amount_thresh > 0.0001:
            logger_file.error("There is something wrong with balance!!! %s != %s", total_amount, amount_thresh)
            raise SystemExit("Balance is not correct!!")

        if total_amount >= min_transfer:
            logger_file.info("Init transferring...")
            logger_file.info("Creating a temporary address...")
            btc_account = self.__create_an_address_with_account_assigned()
            logger_file.info("Starting to move coins to %s", btc_account)

            for received_account, amount in self.coin_to_be_send_dict.iteritems():
                """
                logger_file.info("%s, %s, %f", received_account,
                                 self.btc_rpc_call.get_addresses_by_account(received_account), amount)
                """
                if self.btc_rpc_call.move(received_account, btc_account, float(amount)):
                    pass
                else:
                    logger_file.error("Fail to move coins to from %s to %s!", received_account, btc_account)

            send_to_address = self.yml_config.get_safe_address_to_be_transferred(currency='btc')

            amount_to_transfer = float(total_amount) - 0.001

            logger_file.info("Starting transferring %f coins to address: %s from account: %s", amount_to_transfer,
                             send_to_address, btc_account)

            self.btc_rpc_call.send_from(btc_account, send_to_address, amount_to_transfer)
            logger_file.info("Transfer is done")
        else:
            logger_file.info("It is not ready to do the coin transferring!")


if __name__ == "__main__":
    run_transfer = BTCCurrencyTransfer()
    run_transfer.main()

