from django.test import TestCase
import simplejson as json

from btcrpc.utils import btc_rpc_call
from btcrpc.vo import addresses
from btcrpc.utils.log import *


log = get_log("create new address or addresses tests")


class BTCRPCTestCase(TestCase):

    def setUp(self):
        self.btcRPCCall = btc_rpc_call.BTCRPCCall()

    def test_create_new_address(self):
        for x in xrange(1, 111):
            new_address = self.btcRPCCall.do_get_new_address()
            print new_address

    #python manage.py test btcrpc.test.test_create_new_addr.BTCRPCTestCase.test_serializer_for_creating_new_addresses
    def test_serializer_for_creating_new_addresses(self):
        data = {"addresses": ["mkRRcxbKLpy8zm1K8ARmRZ5gAuPq1ipufM", "mwtg7rSERQRCbsHLnon7dhN86kur5o77V5"], "test": True}
        log.info(type(data))

        addresses_serializer = addresses.NewAddressesSerializer(data=data)
        log.info(addresses_serializer.is_valid())
        log.info(addresses_serializer.errors)

    def test_for_creating_new_addresses(self):
        new_addresses = []
        for x in xrange(0, 10):
            new_address = self.btcRPCCall.do_get_new_address()
            new_addresses.append(new_address)

        for address in new_addresses:
            log.info(address)

        new_addresses_response = addresses.NewAddresses(new_addresses)

        new_addresses_response.test = True
        new_addresses_response.addresses = new_addresses

        log.info(new_addresses_response.addresses)
        log.info(new_addresses_response.test)

        addresses_example_json = json.dumps(new_addresses_response, default=lambda o: o.__dict__)

        log.info(addresses_example_json)
        log.info(type(addresses_example_json))
        log.info(type(new_addresses_response))

        addresses_serializer = addresses.NewAddressesSerializer(data=new_addresses_response.__dict__)
        log.info(addresses_serializer.is_valid())
        log.info(addresses_serializer.errors)
        log.info(addresses_serializer.data)
        #log.info(Response(addresses_serializer.data, status = status.HTTP_400_BAD_REQUEST))
        #log.info(Response(addresses_example_json, status = status.HTTP_400_BAD_REQUEST))