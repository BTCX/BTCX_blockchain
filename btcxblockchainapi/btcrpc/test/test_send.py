__author__ = 'sikamedia'

from django.test import TestCase
from btcrpc.log import *
from btcrpc import btc_rpc_call


log = get_log("send digital currency")


class BTCRPCTestCase(TestCase):

    def setUp(self):
        log.info("init btc wallet")
        self.btc_rpc_call = btc_rpc_call.BTCRPCCall(wallet="send", test=True)

    def test_send(self):
        log.info(self.btc_rpc_call.do_getinfo())