from rest_framework import serializers


class BumpFeePostParametersSerializer(serializers.Serializer):
    wallet = serializers.CharField(max_length=56)
    currency = serializers.CharField(max_length=56)
    txid = serializers.CharField(max_length=64)
    confTarget = serializers.IntegerField(required=False)
    totalFee = serializers.IntegerField(required=False)
    replaceable = serializers.BooleanField(required=False)
    estimate_mode = serializers.CharField(max_length=16, required=False)


class BumpFeeErrorsSerializer(serializers.Serializer):
    error = serializers.CharField(max_length=512)


class BumpFeeSerializer(serializers.Serializer):
    txid = serializers.CharField(max_length=64)
    origfee = serializers.IntegerField()
    fee = serializers.IntegerField()
    errors = BumpFeeErrorsSerializer(many=True)


class BumpFeeErrorSerializer(serializers.Serializer):
    error = serializers.IntegerField()
    error_message = serializers.CharField(max_length=512)
