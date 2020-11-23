from rest_framework import serializers


class GetWalletBalancePostParameterSerializer(serializers.Serializer):

    currency = serializers.CharField(max_length=20)


class WalletBalanceResponseSerializer(serializers.Serializer):

    wallet = serializers.CharField(max_length=32)
    wallet_type = serializers.CharField(max_length=32)
    balance = serializers.DecimalField(
        max_digits=18, decimal_places=8, coerce_to_string=False)
    chain = serializers.IntegerField()
    error = serializers.IntegerField()
    error_message = serializers.CharField(max_length=512, allow_blank=True)


class WalletListField(serializers.ListField):
    child = WalletBalanceResponseSerializer()


class WalletsBalanceResponseSerializer(serializers.Serializer):

    wallets = WalletListField()
