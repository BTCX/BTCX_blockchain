__author__ = 'twan'
__Date__ = '31/08/14'

from rest_framework import serializers


class GetBalancePostParameter(object):

    def __init__(self, currency="btc", address=""):
        self.currency = currency
        self.address = address


class GetBalancePostParametersSerializer(serializers.Serializer):

    currency = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=128)
    #wallet = serializers.CharField()


class GetBalanceResponse(object):

    def __init__(self, balance=0.0, message="", test=False):
        self.balance = balance
        self.message = message
        self.test = test


class GetBalanceResponseSerializer(serializers.Serializer):

    balance = serializers.FloatField()
    message = serializers.CharField(max_length=64)
    test = serializers.BooleanField()