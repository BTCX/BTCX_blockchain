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
import logging
import sys

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
            serializerOutput = addressserializer.AddressOutputSerializer(new_address_output)
            
            return Response(serializerOutput.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BTCCheckAddressReceive(APIView):

     def post(self, request):

        print request.DATA
        serializers = address_receive.AddressReceiveInputSerializer(data=request.DATA)
        if serializers.is_valid():
            log.info(serializers.data["apikey"])
            output_result = address_receive.AddressReceiveInputParaMeter()
            serializeOutput = address_receive.AddressReceiveInputSerializer(output_result)

            return Response(serializers.data, status = status.HTTP_200_OK)
        return Response(serializers.errors, status = status.HTTP_400_BAD_REQUEST)
            


