from rest_framework.response import Response
from rest_framework.views import APIView
from btcrpc.vo.estimate_smart_fee import (
    EstimateSmartFeePostParametersSerializer,
    EstimateSmartFeeSerializer)
from btcrpc.utils.config_file_reader import ConfigFileReader
import logging
from btcrpc.utils.rpc_calls.rpc_instance_generator import RpcGenerator

logger = logging.getLogger(__name__)
yml_config = ConfigFileReader()


class EstimateSmartFee(APIView):

    def post(self, request):
        post_params = EstimateSmartFeePostParametersSerializer(
            data=request.data)
        post_params.is_valid(raise_exception=True)

        currency = post_params.data["currency"]
        wallet = post_params.data["wallet"]
        conf_target = post_params.data["conf_target"]
        estimate_mode = post_params.data.get("estimate_mode")

        rpc_call = RpcGenerator.get_rpc_instance(wallet=wallet,
                                                 currency=currency)
        args = [conf_target, ]
        if estimate_mode:
            args.append(estimate_mode)
        transaction = rpc_call.do_estimate_smart_fee(*args)
        s = EstimateSmartFeeSerializer(transaction)
        return Response(s.data)
