from rest_framework import serializers


class ToSendSerializer(serializers.Serializer):
  amount = serializers.DecimalField(max_digits=16, decimal_places=9, coerce_to_string=True)
  toAddress = serializers.CharField(max_length=128)


class SendManyPostParametersSerializer(serializers.Serializer):
  currency = serializers.CharField(max_length=56)
  toSend = serializers.ListField(child=ToSendSerializer())
  fromAddress = serializers.CharField(max_length=128)
  txFee = serializers.DecimalField(max_digits=16, decimal_places=9, coerce_to_string=True)
  wallet = serializers.CharField(max_length=56)


class SendManyResponse(object):

  def __init__(self, txid, status, fee, message="", test=False):
    self.txid = txid
    self.status = status
    self.fee = fee
    self.message = message
    self.test = test

class SendManyResponseSerializer(serializers.Serializer):
  txid = serializers.CharField(max_length=128)
  status = serializers.CharField(max_length=20)
  fee = serializers.DecimalField(max_digits=16, decimal_places=8, coerce_to_string=True)
  message = serializers.CharField(max_length=256)
  test = serializers.BooleanField()
