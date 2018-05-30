from decimal import Decimal
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from btcrpc.utils import constantutil
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.log import get_log
from btcrpc.vo import wallet_notify
import errno
from bitcoinrpc.authproxy import JSONRPCException
from socket import error as socket_error
from btcrpc.utils.rpc_calls.rpc_instance_generator import RpcGenerator
from btcrpc.utils.chain_enum import ChainEnum

__author__ = 'sikamedia'
__Date__ = '2015-01-18'

log = get_log("WalletNotify view")
yml_config = ConfigFileReader()


class WalletNotify(APIView):
    def post(self, request):
        post_serializers = wallet_notify.GetWalletNotifyPostParameterSerializer(data=request.data)
        chain = ChainEnum.UNKNOWN
        if post_serializers.is_valid():
            currency = post_serializers.data["currency"]
            txid_test = post_serializers.data["txid"]
            wallet_notify_response = \
                wallet_notify.WalletNotifyResponse(chain.value)
            wallet_notify_serializer = wallet_notify.WalletNotifyResponseSerializer(
              data=wallet_notify_response.__dict__)
            if wallet_notify_serializer.is_valid():
                return Response(wallet_notify_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(wallet_notify_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(post_serializers.errors, status=status.HTTP_400_BAD_REQUEST)