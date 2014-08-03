from django.test import TestCase
from btcrpc import btcrpcall
from btcrpc.vo import addresses
import unittest
from btcrpc.log import *


log = get_log("create new address or addresses tests")

class BTCRPCTestCase(TestCase):

    def setUp(self):
        self.btcRPCCall = btcrpcall.BTCRPCall()

    def test_create_new_address(self):
        for x in xrange(1, 111):
            new_address = self.btcRPCCall.do_get_new_address()
            print new_address

    #python manage.py test btcrpc.test.test_create_new_addr.BTCRPCTestCase.test_serializer_for_creating_new_addresses
    def test_serializer_for_creating_new_addresses(self):
        data = {"addresses": ["mkRRcxbKLpy8zm1K8ARmRZ5gAuPq1ipufM", "mwtg7rSERQRCbsHLnon7dhN86kur5o77V5"], "test": True}
        addresses_serializer = addresses.NewAddressesSerializer(data=data)
        log.info(addresses_serializer.is_valid())
        log.info(addresses_serializer.errors)