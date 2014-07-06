from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework import request
from btcrpc.btcrpcall import BTCRPCall
from btcrpc.vo import address, address_receive
from btcrpc.voserializers import addressserializer
from log import *
import simplejson
import logging
import sys
from btcrpc.utils import timeUtil, jsonutil
from vo.api_output_result import *
from vo.confirmation import *

btcRPCcall = BTCRPCall()

log = get_log("btc_rpc")

class BTCGetInfoView(APIView):

    def get(self, request, *args, **kw):
        
        result = btcRPCcall.do_getinfo()
        response = Response(result, status=status.HTTP_200_OK)
        return response

class BTCGetNewAddress(APIView):

    def post(self, request, format=None):
        log.info("what is this")
        print request.DATA
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
        print request.DATA
        serializers = address_receive.AddressReceiveInputSerializer(data=request.DATA)
        if serializers.is_valid():
            log.info(serializers.data[attributeConst.APIKEY])
            amount_input = serializers.data[attributeConst.AMOUNT]
            address_input = serializers.data[attributeConst.ADDRESS]
            currency_input = serializers.data[attributeConst.CURRENCY]
            test_input = serializers.data[attributeConst.TEST]
            
            transactions_log = btcRPCcall.do_list_transactions(address_input)
            print transactions_log[0] #it assumes that this only contains one transaction 
            
            transactions_log_json = simplejson.dumps(transactions_log, use_decimal=True)

            output_result = address_receive.AddressReceiveOutput()

            if jsonutil.JsonUtils.is_json(transactions_log_json):
                transactions_log = transactions_log[0] 
                output_result.txid = transactions_log[attributeConst.TXID]
                output_result.address = transactions_log[attributeConst.ADDRESS]
                output_result.amount = float(transactions_log[attributeConst.AMOUNT])
                output_result.currency = currency_input
                output_result.test = test_input
                output_result.timereceived = \
                    timeUtil.TimeUtils.epoch_to_datetime(transactions_log[attributeConst.TIMERECEIVED])
                output_result.blocktime = \
                    timeUtil.TimeUtils.epoch_to_datetime(transactions_log[attributeConst.BLOCKTIME])

                log.info(BTC_CONFIRMATION)
                if (transactions_log[attributeConst.CONFIRMATIONS] >= BTC_CONFIRMATION): #hard coded
                    output_result.state = STATUS_RECEIVED
                else:
                    output_result.state = STATUS_PENDING
                
                if (float(output_result.amount) != float(amount_input)):
                    output_result.state = STATUS_PENDING
                        
            serializerOutput = address_receive.AddressReceiveOutputSerializer(output_result)

            return Response(serializerOutput.data, status = status.HTTP_200_OK)
        return Response(serializers.errors, status = status.HTTP_400_BAD_REQUEST)
            


