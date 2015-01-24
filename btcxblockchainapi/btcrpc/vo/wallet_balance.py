from decimal import Decimal

__author__ = 'sikamedia'
__Date__ = '2015-01-17'

from rest_framework import serializers


class GetWalletBalancePostParameter(object):

    def __init__(self, currency="btc"):

        self.currency = currency


class GetWalletBalancePostParameterSerializer(serializers.Serializer):

    currency = serializers.CharField(max_length=20)


class WalletBalanceResponse(object):

    def __init__(self, wallet="", balance=Decimal(0), test=False):
        self.wallet = wallet
        self.balance = balance
        self.test = test


class WalletBalanceResponseSerializer(serializers.Serializer):

    wallet = serializers.CharField(max_length=32)
    balance = serializers.DecimalField(max_digits=18, decimal_places=8, coerce_to_string=False)
    test = serializers.BooleanField()


class WalletListField(serializers.ListField):
    child = WalletBalanceResponseSerializer()


class WalletsBalanceResponse(object):

    def __init__(self, wallets=[]):
        self.wallets = wallets


class WalletsBalanceResponseSerializer(serializers.Serializer):

    wallets = WalletListField()

