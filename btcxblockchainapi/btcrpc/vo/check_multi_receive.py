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
    amount = serializers.Decimal()


class PostParametersSerializer(serializers.Serializer):
    transactions = TransactionSerializer(many=True)


class ReceiveInformation(object):
    def __init__(self, api_key="",  currency="btc", address="", received=0.0, risk="low", txids=[]):
        self.api_key = api_key