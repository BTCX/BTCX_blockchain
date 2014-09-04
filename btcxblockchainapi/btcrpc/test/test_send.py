__author__ = 'sikamedia'

from django.test import TestCase
from btcrpc.log import *
from btcrpc import btc_rpc_call
from test_settings import *
from bitcoinrpc.authproxy import JSONRPCException


log = get_log("send digital currency")


class BTCRPCTestCase(TestCase):

    def setUp(self):
        log.info("init btc wallet")
        self.btc_rpc_call = btc_rpc_call.BTCRPCCall(wallet="send")
        self.from_account_balance = self.btc_rpc_call.get_balance(account=FROM_ACCOUNT)

    def test_send_failure(self):

        send_amount = self.from_account_balance + 1
        log.info(float(send_amount))

        try:
            send_response = self.btc_rpc_call.send_from(from_account=FROM_ACCOUNT,
                                                        to_address=TO_ADDRESS, amount=float(send_amount))
        except JSONRPCException as ex:
            log.info("Error: %s" % ex.error['message'])

    def test_send_success(self):

        send_amount = (float(self.from_account_balance) / 100.0)
        log.info("Send amount: %f " % float(send_amount))

        try:
            send_response = self.btc_rpc_call.send_from(from_account=FROM_ACCOUNT,
                                                        to_address=TO_ADDRESS, amount=float(send_amount))

            transaction = self.btc_rpc_call.do_get_transaction(send_response)
            log.info(abs(transaction["fee"]))
        except JSONRPCException as ex:
            log.info("Error: %s" % ex.error['message'])


