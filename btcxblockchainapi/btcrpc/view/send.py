import sherlock
from bitcoinrpc.authproxy import JSONRPCException
from pylibmc import ConnectionError, ServerDown
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from sherlock import MCLock
from sherlock.lock import LockTimeoutException, LockException

from btcrpc.utils import constantutil
from btcrpc.utils.btc_rpc_call import BTCRPCCall
from btcrpc.utils.log import *
from btcrpc.vo import send
from btcrpc.vo.send import *

log = get_log("send currency view")

# define a locker for btcrpc.view.send
lock = MCLock(__name__)
sherlock.configure(expire=120, timeout=20)


class SendCurrencyView(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):

        serializer = send.SendFromPostParametersSerializer(data=request.DATA)

        #from_account_balance = btc_rpc_call.get_balance(account=serializer)

        if serializer.is_valid():

            currency = serializer.data["currency"]
            btc_rpc_call = BTCRPCCall(wallet=serializer.data["wallet"], currency=currency)
            # check is testnet or not
            is_test_net = constantutil.check_service_is_test_net(btc_rpc_call)

            from_account = serializer.data["fromAddress"]
            to_address = serializer.data["toAddress"]
            fee_limit = serializer.data["feeLimit"]
            send_amount = serializer.data["amount"]

            balance = btc_rpc_call.get_balance(account=from_account)

            from_account_is_valid = (btc_rpc_call.do_validate_address(address=from_account))["isvalid"]
            to_address_is_valid = (btc_rpc_call.do_validate_address(address=to_address))["isvalid"]

            if not from_account_is_valid:
                response_serializer = self.__send_to(send_status="NOK",
                                                     message="invalid send from address %s" % from_account,
                                                     test=is_test_net)
                return Response(data=response_serializer.data, status=status.HTTP_406_NOT_ACCEPTABLE)

            if not to_address_is_valid:
                response_serializer = self.__send_to(send_status="NOK",
                                                     message="invalid send to address %s" % to_address,
                                                     test=is_test_net)
                return Response(data=response_serializer.data, status=status.HTTP_406_NOT_ACCEPTABLE)

            if (send_amount + fee_limit) > balance:
                response_serializer = self.__send_to(send_status="NOK",
                                                     message="There is no enough fund from %s" % from_account,
                                                     test=is_test_net)
                return Response(data=response_serializer.data, status=status.HTTP_406_NOT_ACCEPTABLE)

            try:

                if lock.locked() is False:
                    lock.acquire()

                    btc_rpc_call.set_tx_fee(fee_limit)
                    send_response_tx_id = btc_rpc_call.send_from(from_account=from_account,
                                                                 to_address=to_address, amount=float(send_amount))
                    lock.release()

                    transaction = btc_rpc_call.do_get_transaction(send_response_tx_id)
                    log.info(abs(transaction["fee"]))
                    send_response = SendFromResponse(tx_id=send_response_tx_id, status="OK",
                                                     fee=abs(transaction["fee"]), test=is_test_net)
                    send_response_serializer = SendFromResponseSerializer(send_response)
                    return Response(data=send_response_serializer.data, status=status.HTTP_200_OK)
                else:
                    send_response_serializer_NOK = self.__send_to(send_status="NOK",
                                                              message="Distribute lock is taken, send action is blocked",
                                                              test=is_test_net)
            except (JSONRPCException) as ex:
                if lock.locked() is True:
                    lock.release()
                log.info("Error: %s" % ex.error['message'])
                send_response = SendFromResponse(status="NOK", message=ex.error['message'], test=is_test_net)
                send_response_serializer_NOK = SendFromResponseSerializer(send_response)
            except (LockTimeoutException, LockException):
                log.info("Error: %s" % "LockTimeoutException or LockException")
                send_response = SendFromResponse(status="NOK",
                                                 message="LockTimeoutException or LockException",
                                                 test=is_test_net)
                send_response_serializer_NOK = SendFromResponseSerializer(send_response)

            except (ConnectionError, ServerDown):
                log.info("Error: ConnectionError or ServerDown exception")
                send_response = SendFromResponse(status="NOK",
                                                 message="Memcached server might be shutdown, or it is not reachable",
                                                 test=is_test_net)
                send_response_serializer_NOK = SendFromResponseSerializer(send_response)

            return Response(data=send_response_serializer_NOK.data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def __send_to(self, send_status="", message="", test=False):
        response = SendFromResponse(status=send_status, message=message, test=test)
        response_serializer = SendFromResponseSerializer(response)
        return response_serializer
