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


class AddressReceiveOutput(object):
    def __init__(self):
        self._txid = None
        self._state = "pending"
        self._currency = "btc"
        self._amount = 0.0
        self._address = ""
        self._timereceived = None
        self._blocktime = None
        self._message = None
        
    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value

    @property
    def txid(self):
        return self._txid

    @txid.setter
    def txid(self, value):
        self._txid = value

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value):
        self._currency = value

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        self._amount = value

    @property
    def timereceived(self):
        return self._timereceived

    @timereceived.setter
    def timereceived(self, value):
        self._timereceived = value

    @property
    def blocktime(self):
        return self._blocktime

    @blocktime.setter
    def blocktime(self, value):
        self._blocktime = value

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value

class AddressReceiveOutputSerializer(serializers.Serializer):

    txid = serializers.CharField(max_length=200)
    state = serializers.CharField(max_length=15)
    currency = serializers.CharField(max_length=20)
    amount = serializers.FloatField()
    address = serializers.CharField(max_length=200)
    timereceived = serializers.DateTimeField()
    blocktime = serializers.DateTimeField()
    message = serializers.CharField(max_length=200)
    test = serializers.BooleanField()
