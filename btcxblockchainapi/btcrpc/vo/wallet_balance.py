from decimal import Decimal
from btcrpc.utils.chain_enum import ChainEnum

__author__ = 'sikamedia'
__Date__ = '2015-01-17'

from rest_framework import serializers


class GetWalletBalancePostParameter(object):

    def __init__(self, currency="btc"):

        self.currency = currency


class GetWalletBalancePostParameterSerializer(serializers.Serializer):

    currency = serializers.CharField(max_length=20)


class WalletBalanceResponse(object):

    def __init__(self, wallet="", wallet_type="", balance=Decimal(0), chain=ChainEnum.UNKNOWN, error=0, error_message=""):
        self.wallet = wallet
        self.wallet_type = wallet_type
        self.balance = balance
        self.chain = chain
        self.error = error
        self.error_message = error_message


class WalletBalanceResponseSerializer(serializers.Serializer):

    wallet = serializers.CharField(max_length=32)
    wallet_type = serializers.CharField(max_length=32)
    balance = serializers.DecimalField(max_digits=18, decimal_places=8, coerce_to_string=False)
    chain = serializers.IntegerField()
    error = serializers.IntegerField()
    error_message = serializers.CharField(max_length=512, allow_blank=True)

class WalletListField(serializers.ListField):
    child = WalletBalanceResponseSerializer()


class WalletsBalanceResponse(object):

    def __init__(self, wallets=[]):
        self.wallets = wallets


class WalletsBalanceResponseSerializer(serializers.Serializer):

    wallets = WalletListField()

