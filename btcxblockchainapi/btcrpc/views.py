from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework import request
from btcrpc.btcrpcall import BTCRPCall
from btcrpc.vo import address, address_receive, check_receive_transaction
from btcrpc.voserializers import addressserializer
from log import *
import simplejson
import sys
from btcrpc.utils.timeUtil import TimeUtils
from btcrpc.utils.jsonutil import JsonUtils
from vo.api_output_result import *
from vo.confirmation import *

btcRPCcall = BTCRPCall()

log = get_log("btcrpc_view")


class BTCGetInfoView(APIView):

    
    def get(self, request, *args, **kw):
        
        result = btcRPCcall.do_getinfo()
        response = Response(result, status=status.HTTP_200_OK)
        return response


class BTCGetNewAddress(APIView):

    def post(self, request, format=None):
        log.info(request.DATA)
        log.info(request.is_secure())
        serializer = addressserializer.AddressInputSerializer(data=request.DATA)
        
        if serializer.is_valid():
            log.info(serializer.data["apikey"])
            log.info(serializer.data["currency"])
            log.info(serializer.data["test"])
            new_address_output = address.AddressOutputResult()
            new_address =  btcRPCcall.do_get_new_address()
            new_address_output.address = new_address

            #set an account name same as address
            btcRPCcall.do_set_account(new_address,new_address)
            serializerOutput = addressserializer.AddressOutputSerializer(new_address_output)
            return Response(serializerOutput.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BTCCheckAddressReceive(APIView):

     def post(self, request):
        attributeConst = AddressReceiveOutputAttributeConst()
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
            
            received_amount = float(btcRPCcall.do_received_by_address(address_input, confirms_input))
                
            output_result.address = address_input
            output_result.amount = amount_input
            output_result.currency = currency_input
            output_result.test = test_input
            output_result.amountreceived = received_amount

            if amount_input == received_amount:
                output_result.state = STATUS_RECEIVED
                output_result.message = "The amount of btc is received"

            elif amount_input > received_amount:
                output_result.state = STATUS_PENDING
                output_result.message = "You received less"

            else :
                output_result.state = STATUS_RECEIVED
                output_result.message  = "you received more"
                
                        
            serializerOutput = address_receive.AddressReceiveOutputSerializer(output_result)
            return Response(serializerOutput.data, status = status.HTTP_200_OK)

        return Response(serializers.errors, status = status.HTTP_400_BAD_REQUEST)
            

  
class CheckTransaction(APIView):

    def post(self, request, txid):
        log.info(txid)
        attributeConst = AddressReceiveOutputAttributeConst()
        input_serializers = check_receive_transaction.CheckTransactionInputSerializer(data=request.DATA)
        if input_serializers.is_valid():
            log.info(input_serializers.data[attributeConst.APIKEY])
            currency_input = input_serializers.data[attributeConst.CURRENCY]
            test_input = input_serializers.data[attributeConst.TEST]

            check_transaction_log = btcRPCcall.do_get_transaction(txid)
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
                        output_result.state = STATUS_RECEIVED
                    else:
                        output_result.state = STATUS_PENDING
                                    
            else:
                log.info("txid is not valid")
                output_result.txid = txid
                output_result.message = "txid is not valid"
            serializerOutput = check_receive_transaction.CheckTransactionOutputSerializer(output_result)
            return Response(serializerOutput.data, status = status.HTTP_200_OK)        
        return Response(input_serializers.errors, status = status.HTTP_400_BAD_REQUEST)
        
