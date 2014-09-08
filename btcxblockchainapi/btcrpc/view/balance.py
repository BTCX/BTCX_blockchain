__author__ = 'sikamedia'

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from btcrpc.utils.log import *
from btcrpc.utils.btc_rpc_call import *
from btcrpc.vo import balance
from btcrpc.utils import constantutil


log = get_log("send currency view")


class GetBalanceView(APIView):

    @staticmethod
    def post(request):
        log.info(request.DATA)
        log.info(request.is_secure())
        btc_rpc_call = BTCRPCCall(wallet="send")
        #check is testnet or not
        is_test_net = constantutil.check_service_is_test_net(btc_rpc_call)
        serializer = balance.GetBalancePostParametersSerializer(data=request.DATA)

        if serializer.is_valid():

            address_valid = btc_rpc_call.do_validate_address(address=serializer.data["address"])
            if address_valid['isvalid'] is True:
                balance_output = btc_rpc_call.get_balance(account=serializer.data["address"])
                log.info(balance_output)
                balance_output_response = balance.GetBalanceResponse(balance=float(balance_output),
                                                                     message="", test=is_test_net)
                balance_output_response_serializer = balance.GetBalanceResponseSerializer(balance_output_response)
                return Response(data=balance_output_response_serializer.data, status=status.HTTP_200_OK)
            else:
                balance_output_response = balance.GetBalanceResponse(balance=0.0,
                                                                     message="Address is not valid", test=is_test_net)
                balance_output_response_serializer = balance.GetBalanceResponseSerializer(balance_output_response)
                return Response(data=balance_output_response_serializer.data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
