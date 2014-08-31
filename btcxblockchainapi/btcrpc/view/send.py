__author__ = 'sikamedia'

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from log import *

log = get_log("send currency view")

class SendCurrencyView(APIView):

    @staticmethod
    def post(self, request):
        log.info(request.DATA)
        log.info(request.is_secure())