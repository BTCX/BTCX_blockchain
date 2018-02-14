from bitcoinrpc.authproxy import JSONRPCException
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from sherlock import MCLock, LockTimeoutException, LockException
from pylibmc import ConnectionError, ServerDown
from rest_framework import status

from btcrpc.utils import constantutil
from btcrpc.utils.btc_rpc_call import BTCRPCCall
from btcrpc.utils.log import get_log
from btcrpc.vo import send_many_vo
import socket, errno

log = get_log("Bitcoin Send Many:")

# define a locker for send many with a tx fee
lock = MCLock(__name__)


class BTCSendManyView(APIView):
  permission_classes = (IsAdminUser,)

  def post(self, request):
    serializer_post = send_many_vo.SendManyPostParametersSerializer(data=request.data)

    if serializer_post.is_valid():
      log.info(serializer_post.data)
      currency = serializer_post.data["currency"]
      wallet = serializer_post.data["wallet"]
      txFee = serializer_post.data["txFee"]
      btc_rpc_call = BTCRPCCall(wallet=wallet, currency=currency)

      from_account = serializer_post.data['fromAddress']
      log.info(from_account)
      amounts = serializer_post.data['toSend']
      amounts_dict = dict()

      for amount in amounts:
        if amount['toAddress'] in amounts_dict:
          #As the value in amount['toAddress'] is a string, it needs to be converted
          current_amount = float(amounts_dict[amount['toAddress']])
          extra_amount = float(amount['amount'])
          new_amount = current_amount + extra_amount
          amounts_dict[amount['toAddress']] = '%.9f' % new_amount
        else:
          amounts_dict[amount['toAddress']] = amount['amount']

      response = None

      is_test_net = constantutil.check_service_is_test_net(btc_rpc_call)

      try:
        if lock.locked() is False:
          lock.acquire()
          btc_rpc_call.set_tx_fee(txFee)
          isSuccess, result = btc_rpc_call.send_many(from_account=from_account, amounts=amounts_dict)
          lock.release()

          if (isSuccess):
            log.info(result)
            transaction = btc_rpc_call.do_get_transaction(result)
            if transaction is None:
              response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                       fee=0, message="BTC server - " + wallet + "is done.",
                                                       test=is_test_net)

            else:
              response = send_many_vo.SendManyResponse(tx_id=result, status=status.HTTP_200_OK,
                                                       fee=abs(transaction["fee"]), message="Send many is done.",
                                                       test=is_test_net)

          elif result is not None and isinstance(result, JSONRPCException):

            if lock.locked() is True:
              lock.release()
            log.info("Error: %s" % result.error['message'])
            response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                     fee=0, message=result.error['message'], test=is_test_net)
          elif result is not None and isinstance(result, socket.error):
            log.info(result.errno == errno.ECONNREFUSED)
            log.info(result.message)
            response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                     fee=0, message=result.message,
                                                     test=is_test_net)

      except (LockTimeoutException, LockException):
        log.error("Error: %s" % "LockTimeoutException or LockException")
        response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                 fee=0, message="LockTimeoutException or LockException",
                                                 test=is_test_net)
      except (ConnectionError, ServerDown):
        log.error("Error: ConnectionError or ServerDown exception")
        response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                 fee=0, message="Error: ConnectionError or ServerDown exception",
                                                 test=is_test_net)
      if (response is not None):
        send_many_response_serializer = send_many_vo.SendManyResponseSerializer(data=response.__dict__)
      else:
        response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                 fee=0, message="Error: response is None",
                                                 test=is_test_net)
        send_many_response_serializer = send_many_vo.SendManyResponseSerializer(data=response.__dict__)


      if send_many_response_serializer.is_valid():
        return Response(send_many_response_serializer.data, status=status.HTTP_200_OK)
      else:
        return Response(send_many_response_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

    return Response(serializer_post.errors, status=status.HTTP_400_BAD_REQUEST)
