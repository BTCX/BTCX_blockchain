from django.views.generic.base import View, TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import simplejson
from rest_framework import viewsets

from btcrpc.utils.btc_rpc_call import BTCRPCCall
from btcrpc.vo.balance import GetBalancePostParameter
from vo import address, address_receive, check_receive_transaction, addresses, check_multi_receives
from btcrpc.utils.log import *
from utils.timeUtil import TimeUtils
from utils.jsonutil import JsonUtils
from btcrpc.constants.api_output_result import *
from vo.confirmation import *


btc_RPC_Call = BTCRPCCall()
attributeConst = AddressReceiveOutputAttributeConst()
log = get_log("btcrpc_view")

"""
class WalletNotificationView(View):

    def __init__(self):
        self.redis_publisher = RedisPublisher(facility='foo', broadcast=True)

    def get(self, request):
        #data_for_websocket = json.dumps({'some': 'data'})
        #self.redis_publisher.publish_message(RedisMessage(data_for_websocket))
        welcome = RedisMessage('Hello everybody')  # create a welcome message to be sent to everybody
        self.redis_publisher.publish_message(welcome)
"""

class BTCGetInfoView(APIView):
    
    def get(self, request, *args, **kw):
        
        result = btc_RPC_Call.do_getinfo()
        response = Response(result, status=status.HTTP_200_OK)
        return response


class BTCGetNewAddress(APIView):

    def post(self, request, format=None):
        log.info(request.DATA)
        log.info(request.is_secure())
        serializer = address.AddressInputSerializer(data=request.DATA)
        
        if serializer.is_valid():
            log.info(serializer.data["apikey"])
            log.info(serializer.data["currency"])
            log.info(serializer.data["test"])
            new_address_output = address.AddressOutputResult()
            new_address = btc_RPC_Call.do_get_new_address()
            new_address_output.address = new_address

            #set an account name same as address
            btc_RPC_Call.do_set_account(new_address,new_address)
            serializerOutput = address.AddressOutputSerializer(new_address_output)
            return Response(serializerOutput.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BTCCheckAddressReceive(APIView):

    def post(self, request):
        log.info(request.DATA)
        serializers = address_receive.AddressReceiveInputSerializer(data=request.DATA)
        if serializers.is_valid():
            log.info(serializers.data[attributeConst.APIKEY])
            amount_input = float(serializers.data[attributeConst.AMOUNT])
            address_input = serializers.data[attributeConst.ADDRESS]
            currency_input = serializers.data[attributeConst.CURRENCY]
            test_input = serializers.data[attributeConst.TEST]
            confirms_input = serializers.data[attributeConst.MINCONF]

            output_result = address_receive.AddressReceiveOutput()

            address_validation = btc_RPC_Call.do_validate_address(address_input)

            if address_validation["isvalid"] is False:
                output_result.state = STATUS_FAILED
                output_result.address = address_input
                output_result.message = "The address is not valid"
                output_result.test = test_input
                serializer_output = address_receive.AddressReceiveOutputSerializer(output_result)
                return Response(serializer_output.data, status=status.HTTP_400_BAD_REQUEST)
            
            received_amount = float(btc_RPC_Call.amount_received_by_address(address_input, confirms_input))
                
            output_result.address = address_input
            output_result.amount = amount_input
            output_result.currency = currency_input
            output_result.test = test_input
            output_result.amount_received = received_amount

            if amount_input == received_amount:
                output_result.state = STATUS_COMPLETED
                output_result.message = "The amount of btc is completed"

            elif amount_input > received_amount:
                output_result.state = STATUS_PENDING
                output_result.message = "You received less"

            else :
                output_result.state = STATUS_COMPLETED
                output_result.message = "You received more"

            serializer_output = address_receive.AddressReceiveOutputSerializer(output_result)
            return Response(serializer_output.data, status = status.HTTP_200_OK)

        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

"""
class CheckAmountReceived(APIView):

    def post(self, request, address):
        log.info(address)
        log.info(request.is_secure())
        #serializer = addressserializer.AddressInputSerializer(data=request.DATA)
        
        return Response(serializers.errors, status = status.HTTP_400_BAD_REQUEST)
"""


class CheckTransaction(APIView):

    def post(self, request, txid):
        log.info(txid)
        attributeConst = AddressReceiveOutputAttributeConst()
        input_serializers = check_receive_transaction.CheckTransactionInputSerializer(data=request.DATA)
        if input_serializers.is_valid():
            log.info(input_serializers.data[attributeConst.APIKEY])
            currency_input = input_serializers.data[attributeConst.CURRENCY]
            test_input = input_serializers.data[attributeConst.TEST]

            check_transaction_log = btc_RPC_Call.do_get_transaction(txid)
            log.info(check_transaction_log)
            
            
            check_transaction_log_json = simplejson.dumps(check_transaction_log, use_decimal=True)
            
            #log.info(JsonUtils.is_json(check_transaction_log))
            #test_json = simplejson.loads(check_transaction_log)
            #log.info(test_json["error"])
            output_result = check_receive_transaction.CheckTransactionOutput()
            
            if check_transaction_log is not None:
                if JsonUtils.is_json(check_transaction_log_json):
                    log.info(check_transaction_log)
                    log.info(check_transaction_log[attributeConst.DETAILS])
                    log.info(check_transaction_log[attributeConst.DETAILS][0])
                    log.info(check_transaction_log[attributeConst.DETAILS][0][attributeConst.AMOUNT])
                    output_result.txid = check_transaction_log[attributeConst.TXID]
                    output_result.test = test_input
                    output_result.address = check_transaction_log[attributeConst.DETAILS][0][attributeConst.ADDRESS]
                    output_result.currency = currency_input
                    output_result.amount = check_transaction_log[attributeConst.AMOUNT]
                    output_result.blocktime = TimeUtils.epoch_to_datetime(check_transaction_log[attributeConst.BLOCKTIME])
                    output_result.timereceived =  TimeUtils.epoch_to_datetime(check_transaction_log[attributeConst.TIMERECEIVED])
                    if (check_transaction_log[attributeConst.CONFIRMATIONS] >= BTC_CONFIRMATION): #hard coded
                        output_result.state = STATUS_COMPLETED
                    else:
                        output_result.state = STATUS_PENDING
                                    
            else:
                log.info("txid is not valid")
                output_result.txid = txid
                output_result.message = "txid is not valid"
            serializerOutput = check_receive_transaction.CheckTransactionOutputSerializer(output_result)
            return Response(serializerOutput.data, status = status.HTTP_200_OK)        
        return Response(input_serializers.errors, status = status.HTTP_400_BAD_REQUEST)