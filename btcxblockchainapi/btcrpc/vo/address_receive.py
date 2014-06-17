from rest_framework import serializers

class AddressReceiveInputParaMeter(object):
    
    def __init__(self, apikey="", currency="btc", amount=0, address="", test=False):
       
        self._apikey = apikey
        self._currency = currency
        self._amount = amount
        self._address = address
        self._test = test
    
            
    @property
    def apikey(self):
        return self._apikey

    @apikey.setter
    def apikey(self, value):
        self._apikey = value

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value):
        self._currency = value
        
    @property
    def test(self):
        return self._test

    @test.setter
    def test(self, value):
        self._test = value


    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        self._amount = value

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value     

class AddressReceiveInputSerializer(serializers.Serializer):

    apikey = serializers.CharField(max_length=200)
    currency = serializers.CharField(max_length=20)
    test = serializers.BooleanField();
    address = serializers.CharField(max_length=200)
    amount = serializers.FloatField()
