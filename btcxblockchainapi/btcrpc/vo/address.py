
class AddressInputParameter(object):

    def __init__(self, apikey="", currency="btc", test = False):
        self.apikey = apikey
        self.currency = currency
        self.test = test

    @property
    def apikey(self):
        return self.apikey

    @apikey.setter
    def apikey(self, value):
        this.apikey = value

    @property
    def currency(self):
        return this.currency

    @currency.setter
    def currency(self, value):
        this.currency = value
        
    @property
    def test(self):
        return this.test

    @test.setter
    def test(self, value):
        this.test = value

        
class AddressOutputResult(object):
    
    def __init__(self, address=""):
        self.address = address
        
