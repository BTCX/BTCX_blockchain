from decimal import Decimal, ROUND_DOWN
from bitcoinrpc.authproxy import JSONRPCException
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from btcrpc.utils import constantutil
from btcrpc.utils.btc_rpc_call import BTCRPCCall
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.vo import transfers
from rest_framework.response import Response

__author__ = 'sikamedia'
__Date__ = '2015-03-18'


from btcrpc.utils.log import *

log = get_log("Transfer Bitcoin")


class TransferCurrencyView(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):
        post_serializer = transfers.PostParametersSerializer(data=request.DATA)

        # from_account_balance = btc_rpc_call.get_balance(account=serializer)

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

                send_amount = transfer["amount"]
                log.info(send_amount)

                to_address = yml_config.get_safe_address_to_be_transferred(currency=currency)

                log.info("%s, %s, %s, %s" % (currency, from_address,  to_address, send_amount))
                #log.info("%s %s" % currency, from_address)

                from_address_is_valid = (btc_rpc_call.do_validate_address(address=from_address))["isvalid"]
                to_address_is_valid = (btc_rpc_call.do_validate_address(address=to_address))["isvalid"]

                log.info("%s, %s" % (from_address_is_valid, to_address_is_valid))

                if from_address_is_valid and to_address_is_valid:
                    try:

                        send_response_tx_id = btc_rpc_call.send_from(from_account=from_address,
                                                                     to_address=to_address, amount=send_amount)

                        response = transfers.TransferInformationResponse(currency=currency,
                                                                         from_address=from_address,
                                                                         to_address=to_address,
                                                                         amount=Decimal(str(send_amount)),
                                                                         status="ok",
                                                                         txid=send_response_tx_id)

                        response_list.append(response.__dict__)
                    except JSONRPCException as ex:
                        log.info("Error: %s" % ex.error['message'])
                        response = transfers.TransferInformationResponse(currency=currency,
                                                                         from_address=from_address,
                                                                         to_address=to_address,
                                                                         amount=Decimal(str(send_amount)),
                                                                         status="fail",
                                                                         txid="")
                        response_list.append(response.__dict__)

                else:
                    log.info("do nothing")
                    response = transfers.TransferInformationResponse(currency=currency,
                                                                     from_address=from_address,
                                                                     to_address=to_address,
                                                                     amount=Decimal(str(send_amount)),
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

        return Response(post_serializers.errors, status=status.HTTP_400_BAD_REQUEST)