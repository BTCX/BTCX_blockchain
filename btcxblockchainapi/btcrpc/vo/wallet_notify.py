from decimal import Decimal
from btcrpc.utils.chain_enum import ChainEnum

__author__ = 'sikamedia'
__Date__ = '2015-01-17'

from rest_framework import serializers


class GetWalletNotifyPostParameter(object):
    def __init__(self, currency="btc", txid=""):
        self.currency = currency
        self.txid = txid


class GetWalletNotifyPostParameterSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=20)
    txid = serializers.CharField(max_length=128)


class WalletNotifyResponse(object):
    def __init__(self, chain=ChainEnum.UNKNOWN, error=0, error_message=""):
        self.chain = chain
        self.error = error
        self.error_message = error_message


class WalletNotifyResponseSerializer(serializers.Serializer):
    chain = serializers.IntegerField()
    error = serializers.IntegerField()
    error_message = serializers.CharField(max_length=512, allow_blank=True)