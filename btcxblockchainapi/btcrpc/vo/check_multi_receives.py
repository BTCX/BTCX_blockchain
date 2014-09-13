__author__ = 'sikamedia'

from rest_framework import serializers


class PostParameters(object):

    def __init__(self, api_key="", test=True, transactions=[]):

        self.api_key = api_key
        self.test = test
        self.transactions = transactions


class TransactionSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=128)
    amount = serializers.FloatField()


class PostParametersSerializer(serializers.Serializer):
    transactions = TransactionSerializer(many=True)
    test = serializers.BooleanField()



class TransactionIds(object):

    def __init__(self, txids=[]):
        self.txids = txids

class TxIdsField(serializers.WritableField):
    def from_native(self, data):
        if isinstance(data, list):
            return TransactionIds(data)
        else:
            msg = self.error_messages['invalid']
            raise serializers.ValidationError(msg)

    def to_native(self, obj):
        return obj.txids

class ReceiveInformationResponse(object):
    def __init__(self, api_key="",  currency="btc", address="", received=0.0, risk="low", txids=[]):
        self.api_key = api_key
        self.currency = currency
        self.address = address
        self.received = received
        self.risk = risk
        self.txids = txids


class ReceiveInformationResponseSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=128)
    received = serializers.FloatField()
    risk = serializers.CharField(max_length=10) # high, medium, low
    txids = TxIdsField()

