from decimal import Decimal

__author__ = 'sikamedia'
__Date__ = '2015-03-18'


from btcrpc.utils.log import get_log
from rest_framework import serializers

log = get_log("transfers vo")


class PostParameters(object):

    def __init__(self, api_key="", transfers=[]):
        self.api_key = api_key
        self.transfers = transfers


class TransfersSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=20)
    amount = serializers.FloatField()
    from_address = serializers.CharField(max_length=128)
    txFee = serializers.FloatField()


class PostParametersSerializer(serializers.Serializer):
    transfers = TransfersSerializer(many=True)


class TransferInformationResponse(object):
    def __init__(self, currency="btc", from_address="", to_address="", amount=Decimal(0), message="",
                 fee=0.0, status="", txid=""):
        #self.api_key = api_key
        self.currency = currency
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount
        self.message = message
        self.fee = fee
        self.status = status
        self.txid = txid


class TransferInformationResponseSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=20)
    from_address = serializers.CharField(max_length=128)
    to_address = serializers.CharField(max_length=128)
    amount = serializers.DecimalField(max_digits=16, decimal_places=8, coerce_to_string=True)
    fee = serializers.DecimalField(max_digits=18, decimal_places=8, coerce_to_string=True)
    message = serializers.CharField(max_length=256, allow_blank=True)
    status = serializers.CharField(max_length=10)  # ok/fail
    txid = serializers.CharField(max_length=128, allow_blank=True)


class TransfersInformationResponse(object):

    def __init__(self, transfers=[], test=False):
        self.transfers = transfers
        self.test = test


class TransfersInformationResponseSerializer(serializers.Serializer):
    transfers = serializers.ListField(child=TransferInformationResponseSerializer())
    test = serializers.BooleanField()

