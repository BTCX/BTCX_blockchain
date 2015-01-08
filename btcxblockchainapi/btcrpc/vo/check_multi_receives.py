from btcrpc.utils.log import get_log
from decimal import *

__author__ = 'sikamedia'

from rest_framework import serializers


log = get_log("CheckMultiAddressesReceive vo")


class PostParameters(object):

    def __init__(self, api_key="", transactions=[]):
        self.api_key = api_key
        self.transactions = transactions


class TransactionSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=128)
    amount = serializers.FloatField()


class PostParametersSerializer(serializers.Serializer):
    transactions = TransactionSerializer(many=True)

"""
class TransactionIds(object):

    def __init__(self, tx_ids=[]):
        self.txids = tx_ids


class TxIdsField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, list):
            return TransactionIds(data)
        else:
            msg = self.error_messages['invalid']
            raise serializers.ValidationError(msg)

    def to_representation(self, obj):
        return obj.txids
"""


class ReceiveInformationResponse(object):
    def __init__(self, currency="btc", address="", received=0.0, risk="low", txs=[]):
        #self.api_key = api_key
        self.currency = currency
        self.address = address
        self.received = received
        self.risk = risk
        self.txids = txs


class ReceiveInformationResponseSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=128)
    received = serializers.CharField()
    risk = serializers.CharField(max_length=10)  # high, medium, low
    txids = serializers.ListField(child=serializers.CharField(max_length=128))

    class Meta:
        fields = ('currency', 'address', 'received', 'risk', 'txids')


class ReceivesInformationResponse(object):

    def __init__(self, receives=[], test=False):
        self.receives = receives
        self.test = test


class ReceivesInformationResponseSerializer(serializers.Serializer):
    receives = serializers.ListField(child=ReceiveInformationResponseSerializer())
    test = serializers.BooleanField()

"""
class ReceivesInformationResponseSerializer(serializers.Serializer):
    receives = ReceiveInformationResponseSerializer(many=True)
    test = serializers.BooleanField()

    def update(self, attrs, instance=None):

        if instance is not None:
            instance.receives = attrs.get('receives', instance.receives)
            instance.test = attrs.get('test', instance.test)
            return instance
        return ReceivesInformationResponse(**attrs)

    class Meta:
         fields = ('receives', 'test')
"""