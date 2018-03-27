from bitcoinrpc.authproxy import JSONRPCException
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
#from sherlock import MCLock, LockTimeoutException, LockException
from pylibmc import ConnectionError, ServerDown
from rest_framework import status

from btcrpc.utils import constantutil
from btcrpc.utils.log import get_log, log_info, log_error
from btcrpc.vo import send_many_vo
import socket, errno
from socket import error as socket_error
from btcrpc.utils.semaphore import SemaphoreSingleton
from btcrpc.utils.rpc_calls.rpc_instance_generator import RpcGenerator
from btcrpc.utils.chain_enum import ChainEnum

log = get_log("Bitcoin Send Many:")

class BTCSendManyView(APIView):
  permission_classes = (IsAdminUser,)

  def post(self, request):
    log_info(log, "Request data", request.data)
    chain = ChainEnum.UNKNOWN
    semaphore = SemaphoreSingleton()
    serializer_post = send_many_vo.SendManyPostParametersSerializer(data=request.data)

    if serializer_post.is_valid():
      log_info(log, "Post input data", serializer_post.data)
      currency = serializer_post.data["currency"]
      wallet = serializer_post.data["wallet"]
      txFee = serializer_post.data["txFee"]
      from_account = serializer_post.data['fromAddress']
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
      log_info(log, "Amounts to send", amounts_dict)

      response = None

      try:
        rpc_call = RpcGenerator.get_rpc_instance(wallet=wallet, currency=currency)
        log_info(log, "RPC instance class", rpc_call.__class__.__name__)
        chain = constantutil.check_service_chain(rpc_call)
        log_info(log, "Chain", chain.value)

        if (semaphore.acquire_if_released(log)):
          log_info(log, "Trying to set the txfee to", str(txFee))
          txfee_set = rpc_call.set_tx_fee(txFee)
          log_info(log, "Using the suggested txfee " + str(txFee), txfee_set)
          isSuccess, result = rpc_call.send_many(from_account=from_account, amounts=amounts_dict)
          log_info(log, "Is send many request successful", isSuccess)
          log_info(log, "Txid of send many request", result)

          if (isSuccess):
            semaphore.release(log)
            transaction = rpc_call.do_get_transaction(result)
            if transaction is None:
              log_error(log, "The transaction request with the txid:" + result + " did not result in a transaction.")
              response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                       fee=0, message="BTC server - " + wallet + "is done.",
                                                       chain=chain.value, error=1)

            else:
              log_info(log, "Transaction sent", transaction)
              details = transaction["details"]
              details_list = []
              try:
                for transactionDetail in details:
                  if(transactionDetail['category'] == 'send'):
                    details_list.append(self.get_output_details(transactionDetail, result))
                log_info(log, "Details list", details_list)
              except BaseException as e:
                #Since we wan't to make sure that a successfull response actually is sent if the rpc sendmany succeeds
                #we just continue no matter what exception we encounter
                log_error(log, "An error occured when checking the transactions details", e)

              response = send_many_vo.SendManyResponse(tx_id=result, status=status.HTTP_200_OK,
                                                       fee=abs(transaction["fee"]), message="Send many is done.",
                                                       chain=chain.value, error=0, error_message="", details=details_list)

          elif result is not None and isinstance(result, JSONRPCException):
            semaphore.release(log)
            log_error(log, "Error: %s" % result.error['message'])
            response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                     fee=0, message=result.error['message'], chain=chain.value, error=1)
          elif result is not None and isinstance(result, socket.error):
            semaphore.release(log)
            log_error(log, "Error: Is the error an Econnrefused error:", result.errno == errno.ECONNREFUSED)
            log_error(log, "Error message", result.message)
            response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                     fee=0, message=result.message,
                                                     chain=chain.value, error=1)
          else:
            semaphore.release(log)
            log_error(log, "The rpc call was not successfull, result", result)
            response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                     fee=0, message=result,
                                                     chain=chain.value, error=1)
        else:
          log_error(log, "Error: The semaphore is already required, wait until semaphore is released")
          response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                   fee=0, message="Semaphore is already acquired, wait until semaphore"
                                                                  " is released.",
                                                   chain=chain.value, error=1)

      except (ConnectionError, ServerDown):
        semaphore.release(log)
        log_error(log, "Error: ConnectionError or ServerDown exception")
        response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                 fee=0, message="Error: ConnectionError or ServerDown exception",
                                                 chain=chain.value, error=1)

      except JSONRPCException as ex:
        semaphore.release(log)
        log_error(log, "Bitcoin RPC error. Message from python-bitcoinrpc", ex.message)
        error_message = "Bitcoin RPC error, check if username and password for node is correct. Message from " \
                        "python-bitcoinrpc: " + ex.message
        response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                 fee=0, message=error_message,
                                                 chain=chain.value, error=1, error_message=error_message)
      except socket_error as serr:
        semaphore.release(log)
        if serr.errno != errno.ECONNREFUSED:
          error_message = "A general socket error was raised."
          log_error(log, error_message, serr)
          response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                   fee=0, message=error_message,
                                                   chain=chain.value, error=1, error_message=error_message)
        else:
          error_message = "Connection refused error, check if the wallet node is down."
          log_error(log, error_message, serr)
          response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                   fee=0, message=error_message,
                                                   chain=chain.value, error=1, error_message=error_message)
      except BaseException as ex:
        semaphore.release(log)
        error_message = "An exception was raised. Error message: " + str(ex)
        log_error(log, "An exception was raised. Error message", str(ex))
        response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                 fee=0, message=error_message,
                                                 chain=chain.value, error=1, error_message=error_message)
      if response is not None:
        send_many_response_serializer = send_many_vo.SendManyResponseSerializer(data=response.__dict__)
      else:
        log_error(log, "Error: response is None")
        response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                 fee=0, message="Error: response is None",
                                                 chain=chain.value, error=1)
        send_many_response_serializer = send_many_vo.SendManyResponseSerializer(data=response.__dict__)

      log_info(log, "Send many response serializer", send_many_response_serializer)
      if send_many_response_serializer.is_valid():
        log_info(log, "The response send_many_response_serializer was valid. The serializer data is",
                  send_many_response_serializer.data)
        return Response(send_many_response_serializer.data, status=status.HTTP_200_OK)
      else:
        semaphore.release(log)
        log_error(log, "The response send_many_response_serializer was not valid.", send_many_response_serializer.errors)
        return Response(send_many_response_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

    semaphore.release(log)
    return Response(serializer_post.errors, status=status.HTTP_400_BAD_REQUEST)

  def get_output_details(self, transaction_detail, txid):
    return {
      "address" : transaction_detail['address'],
      "txid" : txid,
      "vout" : transaction_detail['vout'],
      "amount" : -transaction_detail['amount']
    }
