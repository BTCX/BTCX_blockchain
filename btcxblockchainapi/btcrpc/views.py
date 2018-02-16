from django.views.generic.base import View, TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import simplejson
from rest_framework import viewsets

from btcrpc.utils.btc_rpc_call import BTCRPCCall
from vo import addresses, check_multi_receives
from btcrpc.utils.log import *
from utils.timeUtil import TimeUtils
from utils.jsonutil import JsonUtils
from btcrpc.constants.api_output_result import *
from vo.confirmation import *


btc_RPC_Call = BTCRPCCall()
attributeConst = AddressReceiveOutputAttributeConst()
log = get_log("btcrpc_view")

class BTCGetInfoView(APIView):
    
    def get(self, request, *args, **kw):
        
        result = btc_RPC_Call.do_getinfo()
        response = Response(result, status=status.HTTP_200_OK)
        return response
