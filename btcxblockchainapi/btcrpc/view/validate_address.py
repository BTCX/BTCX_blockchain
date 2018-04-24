from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from btcrpc.utils import constantutil
from btcrpc.utils.btc_rpc_call import BTCRPCCall
from rest_framework.permissions import IsAdminUser
from bitcoinrpc.authproxy import JSONRPCException
from btcrpc.constants.api_output_result import *

from btcrpc.vo import validate_address
from btcrpc.utils.config_file_reader import ConfigFileReader
import errno
from socket import error as socket_error
import logging
from btcrpc.utils.rpc_calls.rpc_instance_generator import RpcGenerator
from btcrpc.utils.chain_enum import ChainEnum

logger = logging.getLogger(__name__)

yml_config = ConfigFileReader()

class ValidateAddress(APIView):

    def post(self, request):
        chain = ChainEnum.UNKNOWN
        post_serializers = validate_address.ValidateAddressPostParametersSerializer(data=request.data)
        is_mine = False
        is_valid = False
        part_of_wallet = ""

        if post_serializers.is_valid():
            currency = post_serializers.data["currency"]
            address = post_serializers.data["address"]
            wallet_list = yml_config.get_wallet_list(currency)
            try:
                for wallet in wallet_list:
                    rpc_call = RpcGenerator.get_rpc_instance(wallet=wallet, currency=currency)
                    address_validation = rpc_call.do_validate_address(address=address)

                    if address_validation["isvalid"]:
                        chain = constantutil.check_service_chain(rpc_call)
                        is_valid = True
                    else:
                        continue

                    if address_validation["ismine"]:
                        is_mine = True
                        part_of_wallet = wallet

                validate_address_response = validate_address.ValidateAddressResponse(is_valid=is_valid, is_mine=is_mine,
                                                                                     wallet = part_of_wallet,
                                                                                     address = address, chain=chain.value)

            except JSONRPCException as ex:
                logger.error("Error: %s" % ex.error['message'])
                error_message = "Bitcoin RPC error, check if username and password for node is correct. Message from " \
                                "python-bitcoinrpc: " + ex.message
                validate_address_response = validate_address.ValidateAddressResponse(is_valid=is_valid, is_mine=is_mine, wallet = part_of_wallet,
                                                                address = address, chain=chain.value, error=1,
                                                                error_message=error_message)
            except socket_error as serr:
                if serr.errno != errno.ECONNREFUSED:
                    validate_address_response = validate_address.ValidateAddressResponse(is_valid=is_valid, is_mine=is_mine,
                                                                                      wallet = part_of_wallet,
                                                                                      address = address,
                                                                                      chain=chain.value,
                                                                                      error=1,
                                                                                      error_message=
                                                                                      "A general socket error was raised.")
                else:
                    validate_address_response = \
                        validate_address.ValidateAddressResponse(is_valid=is_valid, is_mine=is_mine,
                                                                 wallet=part_of_wallet,
                                                                 address=address,
                                                                 chain=chain.value,
                                               error_message="Connection refused error, check if the wallet node is down.")
            validate_address_serializer = validate_address.ValidateAddressSerializer(data=validate_address_response.__dict__)
            if validate_address_serializer.is_valid():
                return Response(validate_address_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(validate_address_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(post_serializers.errors, status=status.HTTP_400_BAD_REQUEST)