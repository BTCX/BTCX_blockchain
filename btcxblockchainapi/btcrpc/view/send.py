from btcrpc.vo import send

__author__ = 'sikamedia'

from btcrpc.utils.btc_rpc_call import BTCRPCCall
from btcrpc.utils import constantutil
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from btcrpc.utils.log import *

log = get_log("send currency view")


class SendCurrencyView(APIView):



    @staticmethod
    def post(request):

        serializer = send.SendFromPostParametersSerializer(data=request.DATA)

        #from_account_balance = btc_rpc_call.get_balance(account=serializer)

        if serializer.is_valid():

            btc_rpc_call = BTCRPCCall(wallet=serializer.data["wallet"])
             #check is testnet or not
            is_test_net = constantutil.check_service_is_test_net(btc_rpc_call)

            log.info(serializer.data["fromAddress"])


            return Response(data="", status=status.HTTP_200_OK)