from rest_framework.views import APIView
from btcrpc.utils import constantutil
from btcrpc.utils.btc_rpc_call import BTCRPCCall
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.log import get_log
from btcrpc.vo import check_multi_receives
from rest_framework.response import Response
from rest_framework import status
from decimal import *
import simplejson
from rest_framework.parsers import JSONParser
from StringIO import StringIO
from django.http import HttpResponse

__author__ = 'sikamedia'
__Date__ = '2014-09-11'


log = get_log("CheckMultiAddressesReceive view")
yml_config = ConfigFileReader()
risk_low_confirmations = yml_config.get_confirmations_mapping_to_risk(currency='btc', risk='low')
risk_medium_confirmations = yml_config.get_confirmations_mapping_to_risk(currency='btc', risk='medium')
risk_high_confirmations = yml_config.get_confirmations_mapping_to_risk(currency='btc', risk='high')


class CheckMultiAddressesReceive(APIView):

    def post(self, request):
        log.info(request.data)
        post_serializers = check_multi_receives.PostParametersSerializer(data=request.data)
        btc_rpc_call = BTCRPCCall()
        is_test_net = constantutil.check_service_is_test_net(btc_rpc_call)

        response_list = []
        if post_serializers.is_valid():
            log.info(post_serializers.data["transactions"])
            transactions = post_serializers.data["transactions"]
            for transaction in transactions:
                log.info(transaction)

                address_validation = btc_rpc_call.do_validate_address(address=transaction["address"])

                if address_validation["isvalid"] is False:
                    return Response(transaction["address"] + " is not a valid address",
                                    status=status.HTTP_400_BAD_REQUEST)

                received_with_risk = self.__receive_amount_for_risk(wallet_address=transaction["address"],
                                                                    expected_amount=transaction["amount"],
                                                                    btc_service=btc_rpc_call)
                tx_ids = self.__get_txIds(transaction["address"], btc_service=btc_rpc_call)
                log.info(tx_ids)
                log.info(Decimal(received_with_risk["result"]))
                response = check_multi_receives.\
                    ReceiveInformationResponse(currency=transaction["currency"],
                                               address=transaction["address"],
                                               received=Decimal(received_with_risk["result"]),
                                               risk=received_with_risk["risk"],
                                               txs=tx_ids)

                response_list.append(response.__dict__)

            receives_response = check_multi_receives.ReceivesInformationResponse(receives=response_list,
                                                                                 test=is_test_net)
            response_dict = receives_response.__dict__

            response_serializer = check_multi_receives.ReceivesInformationResponseSerializer(data=response_dict)

            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(response_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

        return Response(post_serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def __receive_amount_for_risk(self, wallet_address="", expected_amount=0, btc_service=BTCRPCCall()):

        if not isinstance(btc_service, BTCRPCCall):
            raise TypeError("Expected object BTCRPCCall, got %s" % (type(btc_service),))

        result = float(btc_service.amount_received_by_address(address=wallet_address, confirms=risk_low_confirmations))

        if result >= expected_amount:
            log.info("received with 6 confirmed")
            log.info(result)
            log.info("low")
            return {"result": result, "risk": 'low'}

        result = float(btc_service.amount_received_by_address(address=wallet_address,
                                                              confirms=risk_medium_confirmations))

        if result >= expected_amount:
            log.info("received with 1 confirmed")
            log.info(result)
            log.info("medium")
            return {"result": result, "risk": 'medium'}

        result = float(btc_service.amount_received_by_address(address=wallet_address, confirms=risk_high_confirmations))

        if result >= expected_amount:
            log.info("received with 0 confirmed")
            log.info(result)
            log.info("high")
            return {"result": result, "risk": 'high'}
        else:
            log.info("received amount is not enough")
            log.info(result)
            return {"result": result, "risk": 'high'}


    def __get_txIds(self, account="", btc_service=BTCRPCCall()):

        if not isinstance(btc_service, BTCRPCCall):
            raise TypeError("Expected object BTCRPCCall, got %s" % (type(btc_service),))

        transactions = btc_service.list_transactions(account=account)
        transactions_with_tx_id = []
        for transaction in transactions:
            if 'txid' in transaction:
                transactions_with_tx_id.append(transaction)

        txIds = map(lambda transaction: transaction['txid'], transactions_with_tx_id)
        return txIds