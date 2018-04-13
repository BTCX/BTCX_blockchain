class TransactionDetails(object):
    def __init__(self, to_address="", txid="", vout=0, amount=0.0):
        self.to_address = to_address
        self.txid = txid
        self.vout = vout
        self.amount = amount

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def __dict__(self):
        return {
            "address" : self.to_address,
            "txid" : self.txid,
            "vout" : self.vout,
            "amount" : self.amount
        }