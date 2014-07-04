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

        print request.DATA
        serializers = address_receive.AddressReceiveInputSerializer(data=request.DATA)
        if serializers.is_valid():
            log.info(serializers.data["apikey"])
            amount_input = serializers.data["amount"]
            address_input = serializers.data["address"]

            transactions_log = btcRPCcall.do_list_transactions(address_input)
            print transactions_log[0]
            
            transactions_log_json = simplejson.dumps(transactions_log, use_decimal=True)

            output_result = address_receive.AddressReceiveOutput()
            

            if jsonutil.JsonUtils.is_json(transactions_log_json):
                transactions_log = transactions_log[0] 
                output_result.txid = transactions_log["txid"]
                output_result.address = transactions_log["address"]
                output_result.amount = float(transactions_log["amount"])
                output_result.currency = address_input
                output_result.timereceived = timeUtil.TimeUtils.epoch_to_datetime(transactions_log["timereceived"])
                output_result.blocktime = timeUtil.TimeUtils.epoch_to_datetime(transactions_log["blocktime"])

                if (transactions_log["confirmations"] >= 1): #hard coded
                    output_result.state = "received"
                else:
                    output_result.state = "pending"
                
                if (float(output_result.amount) != float(amount_input)):
                    output_result.state = "error, the received btc is not correct"
                        
            serializerOutput = address_receive.AddressReceiveOutputSerializer(output_result)

            return Response(serializerOutput.data, status = status.HTTP_200_OK)
        return Response(serializers.errors, status = status.HTTP_400_BAD_REQUEST)
            


