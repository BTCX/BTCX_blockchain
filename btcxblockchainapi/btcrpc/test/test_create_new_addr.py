from django.test import TestCase
import btcrpcall
import unittest

class BTCRPCTestCase(TestCase):

    def setUp(self):
        self.btcRPCcall = btcrpcall.BTCRPCall()

    def test_create_new_address(self):
        for x in xrange(1, 111):
            new_address = self.btcRPCcall.do_get_new_address()
            print new_address
