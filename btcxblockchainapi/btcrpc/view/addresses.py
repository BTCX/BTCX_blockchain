from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from btcrpc.utils import constantutil
from btcrpc.utils.btc_rpc_call import BTCRPCCall
from rest_framework.permissions import IsAdminUser
from bitcoinrpc.authproxy import JSONRPCException
from btcrpc.constants.api_output_result import *

from btcrpc.vo import addresses
import errno
from socket import error as socket_error
import logging

__author__ = 'sikamedia'
__Date__ = '2014-09-11'

logger = logging.getLogger(__name__)

attributeConst = AddressReceiveOutputAttributeConst()

class CreateNewAddresses(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):
        serializer_input = addresses.NewAddressesPostParametersSerializer(data=request.data)

        if serializer_input.is_valid():
            try:
                currency = serializer_input.data["currency"]
                wallet = serializer_input.data["wallet"]
                btc_rpc_call = BTCRPCCall(wallet=wallet, currency=currency)
                #check is on testnet or not.
                is_test_net = constantutil.check_service_is_test_net(btc_rpc_call)

                logger.info("quantity is " + str(serializer_input.data["quantity"]) + ".")
                new_addresses = []
                for x in xrange(0, int(serializer_input.data[attributeConst.QUANTITY])):
                    new_address = btc_rpc_call.do_get_new_address()
                    btc_rpc_call.do_set_account(new_address, new_address)
                    new_addresses.append(new_address)

                new_addresses_response = addresses.NewAddresses(addresses=new_addresses, test=is_test_net)

            except JSONRPCException as ex:
                logger.error("Error: %s" % ex.error['message'])
                error_message = "Bitcoin RPC error, check if username and password for node is correct. Message from " \
                                "python-bitcoinrpc: " + ex.message
                new_addresses_response = addresses.NewAddresses(addresses=[], test=True, error=1,
                                                                error_message=error_message)
            except socket_error as serr:
                if serr.errno != errno.ECONNREFUSED:
                    new_addresses_response = addresses.NewAddresses(addresses=[], test=True, error=1,
                                                                    error_message="A general socket error was raised.")
                else:
                    new_addresses_response = \
                        addresses.NewAddresses(addresses=[], test=True, error=1,
                                               error_message="Connection refused error, check if the wallet node is down.")
            addresses_serializer = addresses.NewAddressesSerializer(data=new_addresses_response.__dict__)
            if addresses_serializer.is_valid():
                return Response(addresses_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(addresses_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

        return Response(serializer_input.errors, status=status.HTTP_400_BAD_REQUEST)