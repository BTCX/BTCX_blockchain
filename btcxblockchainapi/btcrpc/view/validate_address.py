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
from btcrpc.utils.log import get_log, log_info, log_error
from btcrpc.utils.rpc_calls.rpc_instance_generator import RpcGenerator
from btcrpc.utils.chain_enum import ChainEnum
from btcrpc.utils.endpoint_timer import EndpointTimer
import requests

log = get_log("CheckWalletsBalance view")

yml_config = ConfigFileReader()


class ValidateAddress(APIView):

    def post(self, request):
        endpoint_timer = EndpointTimer()
        log_info(log, "Request data", request.data)
        chain = ChainEnum.UNKNOWN
        post_serializers = validate_address.ValidateAddressPostParametersSerializer(data=request.data)
        is_mine = False
        is_valid = False
        part_of_wallet = ""

        if post_serializers.is_valid():
            log_info(log, "Post input data", post_serializers.data)
            currency = post_serializers.data["currency"]
            address = post_serializers.data["address"]

            wallet_list = yml_config.get_wallet_list(currency)
            log_info(log, "Wallet list", wallet_list)
            try:
                for index, walletJSON in enumerate(wallet_list):
                    wallet = walletJSON["wallet_name"]
                    rpc_call = RpcGenerator.get_rpc_instance(wallet=wallet, currency=currency)
                    log_info(log, "RPC instance class", rpc_call.__class__.__name__)
                    endpoint_timer.validate_is_within_timelimit()

                    address_validation = rpc_call.do_validate_address(address=address)
                    log_info(log, "Address validation", address_validation)
                    endpoint_timer.validate_is_within_timelimit()

                    if address_validation["isvalid"]:
                        chain = constantutil.check_service_chain(rpc_call)
                        log_info(log, "Chain", chain.value)
                        is_valid = True
                        endpoint_timer.validate_is_within_timelimit()
                    else:
                        continue

                    if address_validation["ismine"]:
                        is_mine = True
                        part_of_wallet = wallet
                        #If the address ismine, then it is also valid.
                        break

                log_info(log, "Is mine is", is_mine)
                log_info(log, "Part of wallet is",
                         part_of_wallet if part_of_wallet != "" else "Not part of any wallet.  ")
                validate_address_response = self.create_validate_address_response_and_log(
                    log_info,
                    "Creating correct validate response",
                    None,
                    is_valid=is_valid,
                    is_mine=is_mine,
                    part_of_wallet=part_of_wallet,
                    address=address,
                    chain=chain)

            except JSONRPCException as ex:
                error_message = "Bitcoin RPC error, check if username and password for node is correct. Message from " \
                                "python-bitcoinrpc: " + ex.message
                validate_address_response = self.create_validate_address_response_and_log(
                    log_error,
                    error_message,
                    ex,
                    is_valid=is_valid,
                    is_mine=is_mine,
                    part_of_wallet=part_of_wallet,
                    address=address,
                    chain=chain,
                    error=1,
                    error_message=error_message)
            except requests.Timeout as ex:
                error_message = "The request timed out. Message from exception: " + str(ex)
                validate_address_response = self.create_validate_address_response_and_log(
                    log_error,
                    error_message,
                    ex,
                    is_valid=is_valid,
                    is_mine=is_mine,
                    part_of_wallet=part_of_wallet,
                    address=address,
                    chain=chain,
                    error=1,
                    error_message=error_message)
            except socket_error as serr:
                error_message = "Socket error: "
                if serr.errno != errno.ECONNREFUSED:
                    error_message = error_message + "A general socket error was raised."
                else:
                    error_message = error_message + "Connection refused error, check if the wallet node is down."
                validate_address_response = self.create_validate_address_response_and_log(
                    log_error,
                    error_message,
                    serr,
                    is_valid=is_valid,
                    is_mine=is_mine,
                    part_of_wallet=part_of_wallet,
                    address=address,
                    chain=chain,
                    error=1,
                    error_message=error_message)
            except BaseException as ex:
                error_message = "An exception was raised. Error message: " + str(ex)
                validate_address_response = self.create_validate_address_response_and_log(
                    log_error,
                    error_message,
                    ex,
                    is_valid=is_valid,
                    is_mine=is_mine,
                    part_of_wallet=part_of_wallet,
                    address=address,
                    chain=chain,
                    error=1,
                    error_message=error_message)

            validate_address_serializer = validate_address.ValidateAddressSerializer(
                data=validate_address_response.__dict__)
            log_info(log, "Validate address serializer", validate_address_serializer)
            if validate_address_serializer.is_valid():
                log_info(log, "Validate serializer was valid")
                return Response(validate_address_serializer.data, status=status.HTTP_200_OK)
            else:
                log_error(log, "New address serializer was invalid", validate_address_serializer.errors)
                return Response(validate_address_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        log_error(log, "The post serializer was incorrect. Post serializer errors", post_serializers.errors)
        return Response(post_serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_validate_address_response_and_log(self, log_function, log_message, log_item, is_valid, is_mine,
                                                 part_of_wallet, address, chain, error=0, error_message=""):
        log_function(log, log_message, log_item)
        validate_address_response = validate_address.ValidateAddressResponse(
            is_valid=is_valid,
            is_mine=is_mine,
            wallet=part_of_wallet,
            address=address,
            chain=chain.value,
            error=error,
            error_message=error_message)
        log_function(log, "The generated validate address response is", validate_address_response.__dict__)
        return validate_address_response
