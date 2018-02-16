from django.views.generic.base import View, TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import simplejson
from rest_framework import viewsets

from btcrpc.utils.btc_rpc_call import BTCRPCCall
from vo import check_receive_transaction, addresses, check_multi_receives
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