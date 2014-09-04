from btcrpc.vo import send

__author__ = 'sikamedia'

from btcrpc.btc_rpc_call import BTCRPCCall
from btcrpc.utils import constantutil
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from btcrpc.log import *

log = get_log("send currency view")


class SendCurrencyView(APIView):

    @staticmethod
    def post(request):
        log.info(request.DATA)
        log.info(request.is_secure())
        btc_rpc_call = BTCRPCCall(wallet="send")

        #check is testnet or not
        is_test_net = constantutil.check_service_is_test_net(btc_rpc_call)

        serializer = send.SendFromPostParametersSerializer(data=request.DATA)