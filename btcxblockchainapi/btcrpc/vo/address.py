class AddressInputParameter(object):

    def __init__(self, apikey="", currency="btc", test=False):
        self._apikey = apikey
        self._currency = currency
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

        
class AddressOutputResult(object):
        
    def __init__(self):
        self._address = None
   
        
    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address= value



    
