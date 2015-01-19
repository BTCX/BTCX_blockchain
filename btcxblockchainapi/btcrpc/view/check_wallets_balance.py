from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from btcrpc.utils.btc_rpc_call import BTCRPCCall
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.log import get_log
from btcrpc.vo import wallet_balance

__author__ = 'sikamedia'
__Date__ = '2015-01-18'

log = get_log("CheckWalletsBalance view")
yml_config = ConfigFileReader()



class CheckWalletsBalance(APIView):

    def post(self, request):
        post_serializers = wallet_balance.GetWalletBalancePostParameterSerializer(data=request.DATA)

        if post_serializers.is_valid():
            currency = post_serializers.data["currency"]
            wallet_list = yml_config.get_wallet_list(currency)
            log.info(wallet_list)

            for wallet in wallet_list:
                log.info(wallet)
            #btc_rpc_call = BTCRPCCall(currency=currency)

        return Response(post_serializers.errors, status=status.HTTP_400_BAD_REQUEST)