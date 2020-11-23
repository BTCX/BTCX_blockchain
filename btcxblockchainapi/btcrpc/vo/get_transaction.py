from rest_framework import serializers


class GetTransactionPostParametersSerializer(serializers.Serializer):
    wallet = serializers.CharField(max_length=56)
    currency = serializers.CharField(max_length=56)
    txid = serializers.CharField(max_length=64)


class GetTransactionDetailsSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=64)
    category = serializers.CharField(max_length=32)
    amount = serializers.DecimalField(max_digits=16, decimal_places=8)
    label = serializers.CharField(max_length=64)
    vout = serializers.IntegerField()
    fee = serializers.DecimalField(max_digits=16, decimal_places=8, required=False)
    abandoned = serializers.BooleanField(required=False)


class GetTransactionSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=16, decimal_places=8)
    fee = serializers.DecimalField(max_digits=16, decimal_places=8, required=False)
    confirmations = serializers.IntegerField()
    blockhash = serializers.CharField(max_length=64)
    blockindex = serializers.IntegerField()
    blocktime = serializers.IntegerField()
    txid = serializers.CharField(max_length=64)
    time = serializers.IntegerField()
    timereceived = serializers.IntegerField()
    bip125_replaceable = serializers.CharField(
        source="bip125-replaceable",max_length=16, required=False)
    details = GetTransactionDetailsSerializer(many=True)
    hex = serializers.CharField(max_length=2048)


class GetTransactionErrorSerializer(serializers.Serializer):
    error = serializers.IntegerField()
    error_message = serializers.CharField(max_length=512)
