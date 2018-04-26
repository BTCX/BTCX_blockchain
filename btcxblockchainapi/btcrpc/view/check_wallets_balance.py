from decimal import Decimal
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from btcrpc.utils import constantutil
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.log import get_log, log_info, log_error
from btcrpc.vo import wallet_balance
from pylibmc import ConnectionError, ServerDown
import errno
from bitcoinrpc.authproxy import JSONRPCException
from socket import error as socket_error
from btcrpc.utils.rpc_calls.rpc_instance_generator import RpcGenerator
from btcrpc.utils.chain_enum import ChainEnum
from btcrpc.utils.endpoint_timer import EndpointTimer
import requests

__author__ = 'sikamedia'
__Date__ = '2015-01-18'

log = get_log("CheckWalletsBalance view")
yml_config = ConfigFileReader()


class CheckWalletsBalance(APIView):
    def post(self, request):
        endpoint_timer = EndpointTimer()
        log_info(log, "Request data", request.data)
        post_serializers = wallet_balance.GetWalletBalancePostParameterSerializer(data=request.data)
        chain = ChainEnum.UNKNOWN

        wallet_balance_response_list = []
        if post_serializers.is_valid():
            log_info(log, "Post input data", post_serializers.data)
            currency = post_serializers.data["currency"]
            wallet_list = yml_config.get_wallet_list(currency)
            log_info(log, "Wallet list", wallet_list)
            for wallet_json in wallet_list:
                log_info(log, "Wallet JSON", wallet_json)
                wallet = wallet_json['wallet_name']
                wallet_type = wallet_json['wallet_type']

                try:
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

                    balance = rpc_call.get_wallet_balance()
                    log_info(log, "Wallet balance", format(balance, '0.8f'))
                    endpoint_timer.validate_is_within_timelimit()

                    wallet_balance_response = \
                        self.create_wallet_balance_response_and_log(
                            log_info,
                            "Generating a successful wallet balance response",
                            None,
                            wallet,
                            wallet_type,
                            balance,
                            chain)
                    self.append_to_wallet_balance_list_and_log(wallet_balance_response_list,
                                                               wallet_balance_response.__dict__)
                except socket_error as serr:
                    error_message = "Socket error: "
                    if serr.errno != errno.ECONNREFUSED:
                        error_message = error_message + "A general socket error was raised"
                    else:
                        error_message = error_message + "Connection refused error, check if the wallet node is down."

                    wallet_balance_response = \
                        self.create_wallet_balance_response_and_log(
                            log_error,
                            error_message,
                            serr,
                            wallet,
                            wallet_type,
                            0,
                            chain,
                            error=1,
                            error_message=error_message)
                    self.append_to_wallet_balance_list_and_log(wallet_balance_response_list,
                                                               wallet_balance_response.__dict__)
                except JSONRPCException as ex:
                    error_message = "Bitcoin RPC error, check if username and password for node is correct. Message from python-bitcoinrpc: " + ex.message
                    wallet_balance_response = \
                        self.create_wallet_balance_response_and_log(
                            log_error,
                            error_message,
                            ex,
                            wallet,
                            wallet_type,
                            0,
                            chain,
                            error=1,
                            error_message=error_message)
                    self.append_to_wallet_balance_list_and_log(wallet_balance_response_list,
                                                               wallet_balance_response.__dict__)
                except requests.Timeout as ex:
                    error_message = "The request timed out. Message from exception: " + str(ex)
                    wallet_balance_response = \
                        self.create_wallet_balance_response_and_log(
                            log_error,
                            error_message,
                            ex,
                            wallet,
                            wallet_type,
                            0,
                            chain,
                            error=1,
                            error_message=error_message)
                    self.append_to_wallet_balance_list_and_log(wallet_balance_response_list,
                                                               wallet_balance_response.__dict__)
                    #We don't want to continue with the next balance check as we need to return the timeout response
                    break
                except BaseException as ex:
                    error_message = "An exception was raised. Error message: " + str(ex)
                    wallet_balance_response = \
                        self.create_wallet_balance_response_and_log(
                            log_error,
                            error_message,
                            ex,
                            wallet,
                            wallet_type,
                            0,
                            chain,
                            error=1,
                            error_message=error_message)
                    self.append_to_wallet_balance_list_and_log(wallet_balance_response_list,
                                                               wallet_balance_response.__dict__)

            wallets_balance_response = wallet_balance.WalletsBalanceResponse(wallets=wallet_balance_response_list)
            log_info(log, "Full wallet balance response", wallets_balance_response.__dict__)

            wallets_balance_response_serializer = \
                wallet_balance.WalletsBalanceResponseSerializer(data=wallets_balance_response.__dict__)
            log_info(log, "Wallet balance response serializer", wallets_balance_response_serializer)

            if wallets_balance_response_serializer.is_valid():
                log_info(log, "The wallet balance response serializer was valid")
                return Response(wallets_balance_response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                log_error(log, "The wallet balance response serializer was not valid",
                          wallets_balance_response_serializer.errors)
                return Response(wallets_balance_response_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

        log_error(log, "The post serializer was incorrect. Post serializer errors", post_serializers.errors)
        return Response(post_serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_wallet_balance_response_and_log(self, log_function, log_message, log_item, wallet, wallet_type, balance,
                                               chain, error=0, error_message=""):
        log_function(log, log_message, log_item)
        wallet_balance_response = wallet_balance.WalletBalanceResponse(
            wallet=wallet,
            wallet_type=wallet_type,
            balance=Decimal(balance),
            chain=chain.value,
            error=error,
            error_message=error_message)
        log_function(log, "The generated wallet balance response is", wallet_balance_response.__dict__)
        return wallet_balance_response

    def append_to_wallet_balance_list_and_log(self, wallet_balance_response_list, wallet_balance_response):
        log_info(log, "Appending the following wallet balance response to the wallet_balance_response_list",
                 wallet_balance_response)
        wallet_balance_response_list.append(wallet_balance_response)
        log_info(log, "wallet_balance_response_list after wallet balance response was appended",
                 wallet_balance_response_list)
