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
from btcrpc.utils.log import get_log, log_info, log_error
from btcrpc.utils.rpc_calls.rpc_instance_generator import RpcGenerator
from btcrpc.utils.chain_enum import ChainEnum
from btcrpc.utils.endpoint_timer import EndpointTimer
import requests

log = get_log("Addresses view")


class CreateNewAddresses(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):
        endpoint_timer = EndpointTimer()
        log_info(log, "Request data", request.data)
        chain = ChainEnum.UNKNOWN
        serializer_input = addresses.NewAddressesPostParametersSerializer(data=request.data)

        if serializer_input.is_valid():
            log_info(log, "Post input data", serializer_input.data)
            new_addresses = []
            try:
                currency = serializer_input.data["currency"]
                wallet = serializer_input.data["wallet"]
                quantity = serializer_input.data["quantity"]

                rpc_call = RpcGenerator.get_rpc_instance(
                    wallet=wallet,
                    currency=currency,
                    endpoint_timer=endpoint_timer
                )
                log_info(log, "RPC instance class", rpc_call.__class__.__name__)
                endpoint_timer.validate_is_within_timelimit()

                chain = constantutil.check_service_chain(rpc_call)
                log_info(log, "Chain", chain.value)
                endpoint_timer.validate_is_within_timelimit()

                number_of_new_addresses = int(quantity)
                log_info(log, "Number of new addresses to create", number_of_new_addresses)

                for x in range(0, number_of_new_addresses):
                    new_address = rpc_call.do_get_new_address(wallet=wallet)
                    log_info(log, "Generated address " + str(x + 1), new_address)
                    endpoint_timer.validate_is_within_timelimit()

                    rpc_call.do_set_account(new_address, new_address)
                    log_info(log, "Setting account for address " + new_address + " to", new_address)
                    endpoint_timer.validate_is_within_timelimit()

                    new_addresses.append(new_address)
                    log_info(log, "new_addresses list after " + new_address + " has been added", new_addresses)

                new_addresses_response = self.create_new_addresses_response_and_log(
                    log_function=log_info,
                    log_message="Generating successful response",
                    log_item=None,
                    new_addresses=new_addresses,
                    chain=chain)

            except JSONRPCException as ex:
                error_message = "Bitcoin RPC error, check if username and password for node is correct. Message from " \
                                "python-bitcoinrpc: " + ex.message
                new_addresses_response = self.create_new_addresses_response_and_log(
                    log_function=log_error,
                    log_message=error_message,
                    log_item=ex,
                    new_addresses=[],
                    chain=chain,
                    error=1,
                    error_message=error_message)
            except requests.Timeout as ex:
                error_message = "The request timed out. Addresses genereated before the timeout " \
                                "is included in the new_addresses list. Message from exception: " + str(ex)
                new_addresses_response = self.create_new_addresses_response_and_log(
                    log_function=log_error,
                    log_message=error_message,
                    log_item=ex,
                    new_addresses=new_addresses,
                    chain=chain,
                    error=1,
                    error_message=error_message)
            except socket_error as serr:
                if serr.errno != errno.ECONNREFUSED:
                    error_message = "A general socket error was raised."
                else:
                    error_message = "Connection refused error, check if the wallet node is down."

                new_addresses_response = self.create_new_addresses_response_and_log(
                    log_function=log_error,
                    log_message=error_message,
                    log_item=serr,
                    new_addresses=[],
                    chain=chain,
                    error=1,
                    error_message=error_message)
            except BaseException as ex:
                error_message = "An exception was raised. Error message: " + str(ex)
                new_addresses_response = self.create_new_addresses_response_and_log(
                    log_function=log_error,
                    log_message=error_message,
                    log_item=ex,
                    new_addresses=[],
                    chain=chain,
                    error=1,
                    error_message=error_message)

            addresses_serializer = addresses.NewAddressesSerializer(data=new_addresses_response.__dict__)
            log_info(log, "New address serializer", addresses_serializer)
            if addresses_serializer.is_valid():
                log_info(log, "New address serializer was valid")
                return Response(addresses_serializer.data, status=status.HTTP_201_CREATED)
            else:
                log_error(log, "New address serializer was invalid", addresses_serializer.errors)
                return Response(addresses_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

        log_error(log, "The post serializer was incorrect. Post serializer errors", serializer_input.errors)
        return Response(serializer_input.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_new_addresses_response_and_log(self, log_function, log_message, log_item, new_addresses, chain, error=0,
                                              error_message=""):
        log_function(log, log_message, log_item)
        new_address_response = addresses.NewAddresses(
            addresses=new_addresses,
            chain=chain.value,
            error=error,
            error_message=error_message)
        log_function(log, "The generated new address response is", new_address_response.__dict__)
        return new_address_response
