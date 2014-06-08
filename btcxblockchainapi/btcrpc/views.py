from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework import request
from btcrpc.btcrpcall import BTCRPCall
from btcrpc.vo import address
from btcrpc.voserializers import addressserializer



btcRPCcall = BTCRPCall()

class BTCGetInfoView(APIView):

    def get(self, request, *args, **kw):
        
        result = btcRPCcall.do_getinfo()
        response = Response(result, status=status.HTTP_200_OK)
        return response

class BTCGetNewAddress(APIView):

    """"
    def get(self, request, *args, **kw):
        result = btcRPCcall.do_get_new_address()
        response = Response(result, status=status.HTTP_200_OK)
        return response
    """

        
    def post(self, request, format=None):
        print request.DATA
        serializer = addressserializer.AddressInputSerializer(data=request.DATA)
        if serializer.is_valid():
            print serializer.data["apikey"]
            print serializer.data["currency"]
            print serializer.data["test"]
            new_address = address.AddressOutputResult()
            #new_address.address = BTCRPCall.do_get_new_address()
            new_address.address = "this is my cool stuff"
            serializerOutput = addressserializer.AddressOutputSerializer(new_address)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


