from django.core.exceptions import RequestDataTooBig
from rest_framework import serializers


class EstimateSmartFeePostParametersSerializer(serializers.Serializer):
    wallet = serializers.CharField(max_length=56)
    currency = serializers.CharField(max_length=56)
    conf_target = serializers.IntegerField()
    estimate_mode = serializers.CharField(max_length=16, required=False)


class EstimateSmartFeeErrorsSerializer(serializers.Serializer):
    error = serializers.CharField(max_length=256)


class EstimateSmartFeeSerializer(serializers.Serializer):
    feerate = serializers.DecimalField(max_digits=16, decimal_places=8)
    errors = EstimateSmartFeeErrorsSerializer(many=True, required=False)
    blocks = serializers.IntegerField()


class EstimateSmartFeeErrorSerializer(serializers.Serializer):
    error = serializers.IntegerField()
    error_message = serializers.CharField(max_length=512)
