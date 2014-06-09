from rest_framework import serializers

class AddressInputSerializer(serializers.Serializer):

    apikey = serializers.CharField(max_length=200)
    currency = serializers.CharField(max_length=20)
    test = serializers.BooleanField();


class AddressOutputSerializer(serializers.Serializer):
    address = serializers.CharField(max_length = 180)
