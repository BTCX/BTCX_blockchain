from decimal import Decimal

from bitcoinrpc.authproxy import JSONRPCException
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from sherlock import MCLock
from sherlock.lock import LockTimeoutException, LockException
from pylibmc import ConnectionError, ServerDown

from btcrpc.utils import constantutil
from btcrpc.utils.btc_rpc_call import BTCRPCCall
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.log import *
from btcrpc.vo import transfers

log = get_log("Transfer Bitcoin")

# define a locker for btcrpc.view.send
lock = MCLock(__name__)


class TransferCurrencyView(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):
        global response_serializer
        post_serializer = transfers.PostParametersSerializer(data=request.data)

        yml_config = ConfigFileReader()

        if post_serializer.is_valid():

            btc_rpc_call = BTCRPCCall()
            is_test_net = constantutil.check_service_is_test_net(btc_rpc_call)

            transfer_list = post_serializer.data["transfers"]
            log.info(is_test_net)
            response_list = []
            for transfer in transfer_list:
                log.info(transfer)
                currency = transfer["currency"]
                from_address = transfer["from_address"]
                txFee = transfer["txFee"]
                send_amount = transfer["amount"]
                log.info(send_amount)

                to_address = yml_config.get_safe_address_to_be_transferred(currency=currency)

                log.info("%s, %s, %s, %s" % (currency, from_address, to_address, send_amount))
                # log.info("%s %s" % currency, from_address)

                from_address_is_valid = (btc_rpc_call.do_validate_address(address=from_address))["isvalid"]
                to_address_is_valid = (btc_rpc_call.do_validate_address(address=to_address))["isvalid"]

                log.info("%s, %s" % (from_address_is_valid, to_address_is_valid))

                # balance = btc_rpc_call.get_balance(account=from_address)

                # canTransfer = (send_amount + txFee) <= balance

                # check if send amount + optional transaction fee > balance
                if from_address_is_valid and to_address_is_valid:
                    try:
                        if lock.locked() is False:
                            lock.acquire()
                            btc_rpc_call.set_tx_fee(txFee)
                            send_response_tx_id = btc_rpc_call.send_from(from_account=from_address,
                                                                         to_address=to_address,
                                                                         amount=send_amount)
                            lock.release()
                            transaction = btc_rpc_call.do_get_transaction(send_response_tx_id)
                            response = transfers.TransferInformationResponse(currency=currency,
                                                                             from_address=from_address,
                                                                             to_address=to_address,
                                                                             amount=Decimal(str(send_amount)),
                                                                             fee=abs(transaction["fee"]),
                                                                             message="Transfer is done",
                                                                             status="ok",
                                                                             txid=send_response_tx_id)

                    except JSONRPCException as ex:
                        if lock.locked() is True:
                            lock.release()
                        log.error("Error: %s" % ex.error['message'])
                        response = transfers.TransferInformationResponse(currency=currency,
                                                                         from_address=from_address,
                                                                         to_address=to_address,
                                                                         amount=Decimal(str(send_amount)),
                                                                         message=ex.error['message'],
                                                                         status="fail",
                                                                         txid="")
                    except (LockTimeoutException, LockException):
                        log.error("Error: %s" % "LockTimeoutException or LockException")
                        response = transfers.TransferInformationResponse(currency=currency,
                                                                         from_address=from_address,
                                                                         to_address=to_address,
                                                                         amount=Decimal(str(send_amount)),
                                                                         message="LockTimeoutException or LockException",
                                                                         status="fail",
                                                                         txid="")
                    except (ConnectionError, ServerDown):
                        log.error("Error: ConnectionError or ServerDown exception")
                        response = transfers.TransferInformationResponse(currency=currency,
                                                                         from_address=from_address,
                                                                         to_address=to_address,
                                                                         amount=Decimal(str(send_amount)),
                                                                         message="Error: ConnectionError or ServerDown exception",
                                                                         status="fail",
                                                                         txid="")

                    response_list.append(response.__dict__)

                else:
                    log.info("do nothing")
                    response = transfers.TransferInformationResponse(currency=currency,
                                                                     from_address=from_address,
                                                                     to_address=to_address,
                                                                     amount=Decimal(str(send_amount)),
                                                                     message="from_address is not valid, " +
                                                                             "or to_address is not valid",
                                                                     status="fail",
                                                                     txid="")
                    response_list.append(response.__dict__)

            log.info(response_list)

            transfers_response = transfers.TransfersInformationResponse(transfers=response_list, test=is_test_net)

            response_dict = transfers_response.__dict__

            response_serializer = transfers.TransfersInformationResponseSerializer(data=response_dict)

            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(response_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
