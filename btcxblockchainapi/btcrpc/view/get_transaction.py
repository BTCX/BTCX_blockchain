from rest_framework.response import Response
from rest_framework.views import APIView
from btcrpc.vo import get_transaction
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.rpc_calls.rpc_instance_generator import RpcGenerator

yml_config = ConfigFileReader()


class GetTransaction(APIView):

    def post(self, request):
        post_params = get_transaction.GetTransactionPostParametersSerializer(data=request.data)
        post_params.is_valid(raise_exception=True)

        wallet = post_params.data["wallet"]
        currency = post_params.data["currency"]
        txid = post_params.data["txid"]

        rpc_call = RpcGenerator.get_rpc_instance(wallet=wallet,
                                                 currency=currency)
        transaction = rpc_call.do_get_transaction(txid=txid)
        s = get_transaction.GetTransactionSerializer(transaction)
        s.is_valid(raise_exception=True)
        return Response(s.data)
