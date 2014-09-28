from django.test import TestCase
from btcrpc.decorator.wallet_secure_decorator import unlock_wallet
from btcrpc.utils.log import get_log

__author__ = 'sikamedia'
__Date__ = '2014-09-28'

log = get_log("send digital currency")

@unlock_wallet
def add(x, y):
    return x + y


class WalletDecoratorTestCase(TestCase):

    def setUp(self):
        pass

    def test_unlock_wallet(self):
        log.info(add.__name__)
        log.info(add.__doc__)
        log.info(add.__module__)
        log.info(str(add(1, 2)))