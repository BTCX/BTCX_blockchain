from btcrpc.utils import btc_rpc_call

from django.test import TestCase
from bitcoinrpc.authproxy import JSONRPCException
from btcrpc.utils.log import *
from test_settings import *
import socket, errno

log = get_log("send many tests")


class BTCSendMany(TestCase):
  def setUp(self):
    log.info("init btc wallet")
    self.btcRPCCall = btc_rpc_call.BTCRPCCall()

  def test_send_many_success(self):

    isSuccess, result = self.btcRPCCall.send_many(from_account=FROM_ACCOUNT_SEND_MANY, amounts=AMOUNTS_1)

    if (isSuccess):
      log.info(result)
    elif result is not None and isinstance(result, JSONRPCException):
      log.info("Error: %s" % result.error['message'])
    elif result is not None and isinstance(result, socket.error):
      log.info(result.errno == errno.ECONNREFUSED)
      log.info(result.message)
    else:
      log.info("Please Check what happens!!!")

  def test_send_many_failure_1(self):

    log.info(type(AMOUNTS_2))

    isSuccess, result = self.btcRPCCall.send_many(from_account=FROM_ACCOUNT_SEND_MANY, amounts=AMOUNTS_2)

    if (isSuccess):
      log.info(result)
    elif result is not None and isinstance(result, JSONRPCException):
      log.info("Error: %s" % result.error['message'])
    elif result is not None and isinstance(result, socket.error):
      log.info(result.errno == errno.ECONNREFUSED)
      log.info(result.message)
    else:
      log.info("Please Check what happens!!!")