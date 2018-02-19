from btcrpc.utils.log import get_log
from datetime import datetime

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
class TxIdTransaction(object):
    def __init__(self, txid, received, confirmations, date=datetime.now()):
        self.txid = txid
        self.received = received
        self.confirmations = confirmations
        self.date = date

class TxIdTransactionSerializer(serializers.Serializer):
    txid = serializers.CharField(max_length=128)
    received = serializers.DecimalField(max_digits=18, decimal_places=12, coerce_to_string=True)
    confirmations = serializers.IntegerField()
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

class ReceiveInformationResponse(object):
    def __init__(self, currency="btc", address="", received=0.0, risk="low", txs=[], error=0, error_message=""):
        #self.api_key = api_key
        self.currency = currency
        self.address = address
        self.received = received
        self.risk = risk
        self.txids = txs
        self.error = error
        self.error_message = error_message


class ReceiveInformationResponseSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=20, allow_blank=True)
    address = serializers.CharField(max_length=128, allow_blank=True)
    received = serializers.DecimalField(max_digits=18, decimal_places=12, coerce_to_string=True)
    risk = serializers.CharField(max_length=10, allow_blank=True)  # high, medium, low
    txids = TxIdTransactionSerializer(many=True)

    class Meta:
        fields = ('currency', 'address', 'received', 'risk', 'txids', 'error', 'error_message')


class ReceivesInformationResponse(object):

    def __init__(self, receives=[], test=False, error=0, error_message=""):
        self.receives = receives
        self.test = test
        self.error = error
        self.error_message = error_message


class ReceivesInformationResponseSerializer(serializers.Serializer):
    receives = serializers.ListField(child=ReceiveInformationResponseSerializer())
    test = serializers.BooleanField()
    error = serializers.IntegerField()
    error_message = serializers.CharField(max_length=512, allow_blank=True)

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