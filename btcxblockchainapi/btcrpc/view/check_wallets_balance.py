from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from btcrpc.utils import constantutil
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.vo.wallet_balance import (
    GetWalletBalancePostParameterSerializer,
    WalletsBalanceResponseSerializer)
from btcrpc.utils.rpc_calls.rpc_instance_generator import RpcGenerator
from btcrpc.utils.chain_enum import ChainEnum
import logging

log = logging.getLogger(__name__)
yml_config = ConfigFileReader()


class CheckWalletsBalance(APIView):

    def post(self, request):
        post_serializers = GetWalletBalancePostParameterSerializer(
            data=request.data)
        post_serializers.is_valid(raise_exception=True)

        chain = ChainEnum.UNKNOWN
        wallet_balance_response_list = []
        currency = post_serializers.data["currency"]
        wallet_list = yml_config.get_wallet_list(currency)
        log.info(wallet_list)

        for wallet_json in wallet_list:
            wallet = wallet_json["wallet_name"]
            wallet_type = wallet_json["wallet_type"]

            log.info(wallet)
            rpc_call = RpcGenerator.get_rpc_instance(wallet=wallet,
                                                     currency=currency)
            chain = constantutil.check_service_chain(rpc_call)
            log.info(chain)
            balance = rpc_call.get_wallet_balance()
            log.info(format(balance, "0.8f"))
            wallet_balance_response = {
                "wallet": wallet,
                "wallet_type": wallet_type,
                "balance": Decimal(balance),
                "chain": chain.value,
                "error": 0,
                "error_message": ""}

            log.info(wallet_balance_response)
            wallet_balance_response_list.append(wallet_balance_response)

        s = WalletsBalanceResponseSerializer(
            data={"wallets": wallet_balance_response_list})
        s.is_valid(raise_exception=True)
        return Response(s.data)
