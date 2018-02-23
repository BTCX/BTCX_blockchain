from bitcoinrpc.authproxy import JSONRPCException
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
#from sherlock import MCLock, LockTimeoutException, LockException
from pylibmc import ConnectionError, ServerDown
from rest_framework import status

from btcrpc.utils import constantutil
from btcrpc.utils.btc_rpc_call import BTCRPCCall
from btcrpc.utils.log import get_log
from btcrpc.vo import send_many_vo
import socket, errno
from socket import error as socket_error
from btcrpc.utils.semaphore import SemaphoreSingleton

log = get_log("Bitcoin Send Many:")

# define a locker for send many with a tx fee
#lock = MCLock(__name__)

class BTCSendManyView(APIView):
  permission_classes = (IsAdminUser,)

  def post(self, request):
    semaphore = SemaphoreSingleton()
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
          #As the values in amounts_dict[amount['toAddress']] and amount['amount'] is a string, They need to be converted
          current_amount = float(amounts_dict[amount['toAddress']])
          extra_amount = float(amount['amount'])
          new_amount = current_amount + extra_amount
          amounts_dict[amount['toAddress']] = '%.9f' % new_amount
        else:
          amounts_dict[amount['toAddress']] = amount['amount']

      response = None

      try:

        is_test_net = constantutil.check_service_is_test_net(btc_rpc_call)

        if (semaphore.acquire_if_released()):
          btc_rpc_call.set_tx_fee(txFee)
          isSuccess, result = btc_rpc_call.send_many(from_account=from_account, amounts=amounts_dict)


          if (isSuccess):
            semaphore.release()
            transaction = btc_rpc_call.do_get_transaction(result)
            if transaction is None:
              response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                       fee=0, message="BTC server - " + wallet + "is done.",
                                                       test=is_test_net, error=1)

            else:
              response = send_many_vo.SendManyResponse(tx_id=result, status=status.HTTP_200_OK,
                                                       fee=abs(transaction["fee"]), message="Send many is done.",
                                                       test=is_test_net)

          elif result is not None and isinstance(result, JSONRPCException):
            semaphore.release()
            log.info("Error: %s" % result.error['message'])
            response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                     fee=0, message=result.error['message'], test=is_test_net, error=1)
          elif result is not None and isinstance(result, socket.error):
            semaphore.release()
            log.info(result.errno == errno.ECONNREFUSED)
            log.info(result.message)
            response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                     fee=0, message=result.message,
                                                     test=is_test_net, error=1)
        else:
          response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                   fee=0, message="Semaphore is already acquired, wait until semaphore"
                                                                  " is released.",
                                                   test=True, error=1)

      except (ConnectionError, ServerDown):
        semaphore.release()
        log.error("Error: ConnectionError or ServerDown exception")
        response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                 fee=0, message="Error: ConnectionError or ServerDown exception",
                                                 test=True, error=1)

      except JSONRPCException as ex:
        semaphore.release()
        log.error("Error: %s" % ex.error['message'])
        error_message = "Bitcoin RPC error, check if username and password for node is correct. Message from " \
                        "python-bitcoinrpc: " + ex.message
        response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                 fee=0, message=error_message,
                                                 test=True, error=1, error_message=error_message)
      except socket_error as serr:
        semaphore.release()
        if serr.errno != errno.ECONNREFUSED:
          error_message = "A general socket error was raised."
          response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                   fee=0, message=error_message,
                                                   test=True, error=1, error_message=error_message)
        else:
          error_message = "Connection refused error, check if the wallet node is down."
          response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                   fee=0, message=error_message,
                                                   test=True, error=1, error_message=error_message)

      if (response is not None):
        send_many_response_serializer = send_many_vo.SendManyResponseSerializer(data=response.__dict__)
      else:
        is_test_net = constantutil.check_service_is_test_net(btc_rpc_call)
        response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                 fee=0, message="Error: response is None",
                                                 test=is_test_net, error=1)
        send_many_response_serializer = send_many_vo.SendManyResponseSerializer(data=response.__dict__)


      if send_many_response_serializer.is_valid():
        return Response(send_many_response_serializer.data, status=status.HTTP_200_OK)
      else:
        return Response(send_many_response_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

    return Response(serializer_post.errors, status=status.HTTP_400_BAD_REQUEST)
