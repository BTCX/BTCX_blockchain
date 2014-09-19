from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient
from btcrpc.test.test_settings import USER_NAME, PASSWORD, FROM_ACCOUNT
from btcrpc.utils.log import get_log
from django.test import TestCase

__author__ = 'sikamedia'
__Date__ = '2014-09-19'


log = get_log("web API test - Balance")


class BTCRPCTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        log.info("login...")
        log.info(USER_NAME)
        log.info(PASSWORD)
        self.user = User.objects.create_superuser(USER_NAME, email='testuser@test.com', password=PASSWORD)
        self.user.save()
        self.login_client = self.client.login(username=USER_NAME, password=PASSWORD)
        log.info(self.login_client)

    def tearDown(self):
        log.info("log out...")
        #self.client.logout()

    def get_balance_test(self):
        response = self.client.post('/api/v1/balance/', {"currency": "btc", "address": FROM_ACCOUNT}, format='json')
        log.info(response.content)




