from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from rest_framework import request
from btcrpc.btcrpcall import BTCRPCall

btcRPCcall = BTCRPCall()

class BTCGetInfoView(APIView):

    def get(self, request, *args, **kw):
        
        result = btcRPCcall.do_getinfo()
        response = Response(result, status=status.HTTP_200_OK)
        return response

class BTCGetNewAddress(APIView):

    def get(self, request, *args, **kw):
        result = btcRPCcall.do_get_new_address()
        response = Response(result, status=status.HTTP_200_OK)
        return response
        
        



