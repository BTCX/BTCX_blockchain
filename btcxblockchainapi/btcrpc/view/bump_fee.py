from rest_framework.response import Response
from rest_framework.views import APIView
from btcrpc.vo.bump_fee import (
    BumpFeeSerializer, BumpFeePostParametersSerializer)
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.rpc_calls.rpc_instance_generator import RpcGenerator
import logging

logger = logging.getLogger(__name__)
yml_config = ConfigFileReader()


class BumpFee(APIView):

    def post(self, request):
        post_params = BumpFeePostParametersSerializer(data=request.data)
        post_params.is_valid(raise_exception=True)

        currency = post_params.data["currency"]
        wallet = post_params.data["wallet"]
        txid = post_params.data["txid"]

        options = {}
        for k in ("confTarget", "totalFee", "replaceable", "estimate_mode"):
            if k in post_params.data:
                options.update({k: post_params.data[k]})

        rpc_call = RpcGenerator.get_rpc_instance(
            wallet=wallet, currency=currency)
        transaction = rpc_call.do_bump_fee(txid, options)
        s = BumpFeeSerializer(transaction)
        s.is_valid(raise_exception=True)
        return Response(s.data)
