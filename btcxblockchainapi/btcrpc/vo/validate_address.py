from rest_framework import serializers
from btcrpc.utils.chain_enum import ChainEnum

__author__ = 'twan'


class ValidateAddressPostParameters(object):
    def __init__(self, currency="btc", address=""):
        self.currency = currency
        self.address = address


class ValidateAddressPostParametersSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=64)


class ValidateAddressResponse(object):
    def __init__(self, is_valid, is_mine, wallet, address, chain, error=0, error_message=""):
        self.is_valid = is_valid
        self.is_mine = is_mine
        self.address = address
        self.wallet = wallet
        self.chain = chain
        self.error = error
        self.error_message = error_message


class ValidateAddressSerializer(serializers.Serializer):
    is_valid = serializers.BooleanField()
    is_mine = serializers.BooleanField()
    address = serializers.CharField(max_length=64, allow_blank=True)
    wallet = serializers.CharField(max_length=32, allow_blank=True)
    chain = serializers.IntegerField()
    error = serializers.IntegerField()
    error_message = serializers.CharField(max_length=512, allow_blank=True)

