from rest_framework.test import APIRequestFactory
from btcrpc.utils.log import get_log
from django.test import TestCase

__author__ = 'sikamedia'
__Date__ = '2014-09-19'


log = get_log("web API test - Balance")


class BTCRPCTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
