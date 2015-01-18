from rest_framework.views import APIView
from btcrpc.utils.btc_rpc_call import BTCRPCCall
from btcrpc.utils.log import get_log
from btcrpc.vo import wallet_balance

__author__ = 'sikamedia'
__Date__ = '2015-01-18'

log = get_log("Check all wallets' balance view")


class CheckWalletsBalance(APIView):

    def post(self, request):
        post_serializers = wallet_balance.GetWalletBalancePostParameterSerializer(data=request.DATA)

        if post_serializers.is_valid():
            currency = post_serializers.data["currency"]
            btc_rpc_call = BTCRPCCall(currency=currency)