from rest_framework import serializers

__author__ = 'twan'


class NewAddressesPostParameters(object):

    def __init__(self, api_key="not_used", currency="btc", quantity=1, wallet=""):
        self._api_key = api_key
        self._currency = currency
        self._quantity = quantity
        self._wallet = wallet

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value


    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value):
        self._currency = value

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        self._quantity = value


class NewAddressesPostParametersSerializer(serializers.Serializer):

    #api_key = serializers.CharField(max_length=200)
    currency = serializers.CharField(max_length=20)
    quantity = serializers.IntegerField(max_value=50)
    wallet = serializers.CharField()


class NewAddress(object):

    def __init__(self):
        self._address = None


    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value


class NewAddressSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=180)


class NewAddresses(object):

    #addresses = []

    def __init__(self, addresses=[], test=False):
        self.addresses = addresses
        self.test = test


    @property
    def _addresses(self):
        return self.addresses

    @_addresses.setter
    def set_addresses(self, value):
        self.addresses = value

    @property
    def _test(self):
        return self._test

    @_test.setter
    def set_test(self, value):
        self._test = value


class AddressesField(serializers.WritableField):
    def from_native(self, data):
        if isinstance(data, list):
            return NewAddresses(data)
        else:
            msg = self.error_messages['invalid']
            raise serializers.ValidationError(msg)

    def to_native(self, obj):
        return obj.addresses


#check http://stackoverflow.com/questions/17289039/how-can-i-define-a-list-field-in-django-rest-framework
class NewAddressesSerializer(serializers.Serializer):
    test = serializers.BooleanField()
    addresses = AddressesField()



