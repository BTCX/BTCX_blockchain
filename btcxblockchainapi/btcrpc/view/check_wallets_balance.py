from decimal import Decimal
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from btcrpc.utils import constantutil
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.log import get_log
from btcrpc.vo import wallet_balance
from pylibmc import ConnectionError, ServerDown
import errno
from bitcoinrpc.authproxy import JSONRPCException
from socket import error as socket_error
from btcrpc.utils.rpc_calls.rpc_instance_generator import RpcGenerator
from btcrpc.utils.chain_enum import ChainEnum

__author__ = 'sikamedia'
__Date__ = '2015-01-18'

log = get_log("CheckWalletsBalance view")
yml_config = ConfigFileReader()


class CheckWalletsBalance(APIView):

    def post(self, request):
        post_serializers = wallet_balance.GetWalletBalancePostParameterSerializer(data=request.data)
        chain = ChainEnum.UNKNOWN

        wallet_balance_response_list = []
        if post_serializers.is_valid():
            currency = post_serializers.data["currency"]
            wallet_list = yml_config.get_wallet_list(currency)
            log.info(wallet_list)
            for wallet in wallet_list:
                try:
                    log.info(wallet)
                    rpc_call = RpcGenerator.get_rpc_instance(wallet=wallet, currency=currency)
                    chain = constantutil.check_service_chain(rpc_call)
                    log.info(chain)
                    balance = rpc_call.get_wallet_balance()
                    log.info(format(balance, '0.8f'))
                    wallet_balance_response = wallet_balance.WalletBalanceResponse(wallet=wallet,
                                                                                   balance=Decimal(balance),
                                                                                   chain=chain.value)

                    log.info(wallet_balance_response.__dict__)
                    wallet_balance_response_list.append(wallet_balance_response.__dict__)
                except socket_error as serr:
                    if serr.errno != errno.ECONNREFUSED:
                        wallet_balance_response = wallet_balance.WalletBalanceResponse(wallet=wallet,
                                                                                       balance=Decimal(0),
                                                                                       chain=chain.value,
                                                                                       error=1,
                                                                                       error_message="A general socket error was raised.")
                        wallet_balance_response_list.append(wallet_balance_response.__dict__)
                    else:
                        wallet_balance_response = wallet_balance.WalletBalanceResponse(wallet=wallet,
                                                                                       balance=Decimal(0),
                                                                                       chain=chain.value,
                                                                                       error=1,
                                                                                       error_message="Connection refused error, check if the wallet node is down.")
                        wallet_balance_response_list.append(wallet_balance_response.__dict__)
                except JSONRPCException as ex:
                    wallet_balance_response = wallet_balance.WalletBalanceResponse(wallet=wallet,
                                                                                   balance=Decimal(0),
                                                                                   chain=chain.value,
                                                                                   error=1,
                                                                                   error_message="Bitcoin RPC error, check if username and password for node is correct. Message from python-bitcoinrpc: " + ex.message)
                    wallet_balance_response_list.append(wallet_balance_response.__dict__)


            wallets_balance_response = wallet_balance.WalletsBalanceResponse(wallets=wallet_balance_response_list)

            wallets_balance_response_serializer = \
                wallet_balance.WalletsBalanceResponseSerializer(data=wallets_balance_response.__dict__)

            if wallets_balance_response_serializer.is_valid():
                return Response(wallets_balance_response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(wallets_balance_response_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

        return Response(post_serializers.errors, status=status.HTTP_400_BAD_REQUEST)