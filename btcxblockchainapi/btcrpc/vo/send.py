__author__ = 'twan'
from rest_framework import serializers


class SendFromPostParameter(object):

    def __init__(self, api_key="", currency="", amount=0, from_address="", to_address="", test=True,
                 fee_limit=0.0, wallet=""):
        self.api_key = api_key
        self.currency = currency
        self.amount = amount
        self.fromAddress = from_address
        self.toAddress = to_address
        self.test = test
        self.feeLimit=fee_limit
        self.wallet = wallet


class PostParametersSerializer(serializers.Serializer):

    currency = serializers.CharField(max_length=20)
    amount = serializers.FloatField()
    fromAddress = serializers.CharField(max_length=128)
    toAddress = serializers.CharField(max_length=128)
    test = serializers.BooleanField()
    feeLimit = serializers.FloatField()
    wallet = serializers.CharField()


class SendFromResponse(object):

    def __init__(self, tx_id="", status="", fee=0.0, message=""):
        self.txid = tx_id
        self.status = status
        self.fee = fee
        self.message = message


class SendFromResponseSerializer(serializers.Serializer):
    txid = serializers.CharField(max_length=128)
    status = serializers.CharField(max_length=16)
    fee = serializers.FloatField()
    message = serializers.CharField(max_length=64)
