from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from sherlock import MCLock
from rest_framework import status

from btcrpc.utils import constantutil
from btcrpc.utils.btc_rpc_call import BTCRPCCall
from btcrpc.utils.log import get_log
from btcrpc.vo import send_many_vo

log = get_log("Bitcoin Send Many:")

# define a locker for send many with a tx fee
lock = MCLock(__name__)


class BTCSendManyView(APIView):
  permission_classes = (IsAdminUser,)

  def post(self, request):
    serializer_post = send_many_vo.SendManyPostParametersSerializer(data=request.DATA)

    if serializer_post.is_valid():
      log.info(serializer_post.data)
      currency = serializer_post.data["currency"]
      wallet = serializer_post.data["wallet"]
      btc_rpc_call = BTCRPCCall(wallet=wallet, currency=currency)
      is_test_net = constantutil.check_service_is_test_net(btc_rpc_call)

      from_account = serializer_post.data['fromAddress']
      log.info(from_account)
      amounts = serializer_post.data['toSend']

      amounts_dict = dict()

      for amount in amounts:
        amounts_dict[amount['toAddress']] = amount['amount']

      log.info(amounts_dict)
      tx_id = btc_rpc_call.send_many(from_account=from_account, amounts=amounts_dict)

      log.info(tx_id)

    return Response(serializer_post.errors, status=status.HTTP_400_BAD_REQUEST)
