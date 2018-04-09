from decimal import Decimal

from btcrpc.utils.log import get_log
from rest_framework import serializers
from btcrpc.utils.chain_enum import ChainEnum

log = get_log(__file__)

class PostParameters(object):

    def __init__(self, api_key="", transfers=[]):
        self.api_key = api_key
        self.transfers = transfers


class TransfersSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=20)
    amount = serializers.FloatField()
    txFee = serializers.DecimalField(max_digits=16, decimal_places=9, coerce_to_string=False, required=False, default=0.0)
    wallet = serializers.CharField(max_length=20)
    safe_address = serializers.CharField(max_length=128)


class PostParametersSerializer(serializers.Serializer):
    transfers = TransfersSerializer(many=True)


class TransactionWithFeeInformationResponse(object):
    def __init__(self, txid="", fee=0.0):
        self.fee = fee
        self.txid = txid


class TransactionWithFeeInformationResponseSerializer(serializers.Serializer):
    fee = serializers.DecimalField(max_digits=18, decimal_places=8, coerce_to_string=False)
    txid = serializers.CharField(max_length=128, allow_blank=True)


class TransferInformationResponse(object):
    def __init__(self, currency="btc", to_address="", amount=Decimal(0), message="",
                 status="", transaction_fee_infos=[]):
        self.currency = currency
        self.to_address = to_address
        self.amount = amount
        self.message = message
        self.status = status
        self.transactions = transaction_fee_infos


class TransferInformationResponseSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=20)
    to_address = serializers.CharField(max_length=128)
    amount = serializers.DecimalField(max_digits=16, decimal_places=8, coerce_to_string=False)
    message = serializers.CharField(max_length=256, allow_blank=True)
    status = serializers.CharField(max_length=10)  # ok/fail
    transactions = serializers.ListField(child=TransactionWithFeeInformationResponseSerializer())


class TransfersInformationResponse(object):

    def __init__(self, transfers=[], chain=ChainEnum.UNKNOWN, error=0, error_message=""):
        self.transfers = transfers
        self.chain = chain
        self.error = error
        self.error_message = error_message


class TransfersInformationResponseSerializer(serializers.Serializer):
    transfers = serializers.ListField(child=TransferInformationResponseSerializer())
    chain = serializers.IntegerField()
    error = serializers.IntegerField()
    error_message = serializers.CharField(max_length=512, allow_blank=True)