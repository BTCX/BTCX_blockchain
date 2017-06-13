from btcrpc.utils import btc_rpc_call

from django.test import TestCase
from bitcoinrpc.authproxy import JSONRPCException
from btcrpc.utils.log import *
from test_settings import *
import socket, errno

log = get_log("send many tests")


class BTCRPCSENDMANY(TestCase):
    def setUp(self):
        log.info("init btc wallet")
        self.btcRPCCall = btc_rpc_call.BTCRPCCall()

    def test_send_many_success(self):

        isSuccess, result = self.btcRPCCall.send_many(from_account=FROM_ACCOUNT, amounts=AMOUNTS)

        if (isSuccess):
            log.info(result)
        elif result is not None and isinstance(result, JSONRPCException):
            log.info("Error: %s" % result.error['message'])
        elif result is not None and isinstance(result, socket.error):
            log.info(result.errno == errno.ECONNREFUSED)
            log.info(result.message)
        else:
            log.info("Please Check what happens!!!")