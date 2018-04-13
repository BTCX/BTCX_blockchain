class TransactionDetails(object):
    def __init__(self, to_address="", txid="", vout=-1, amount=0.0):
        self.to_address = to_address
        self.txid = txid
        self.vout = vout
        self.amount = amount

    def __str__(self):
        return self.get_self_str()

    def __repr__(self):
        return self.get_self_str()

    def get_self_str(self):
        return "{'address': '" + self.to_address + "', 'txid': '" + self.txid + "',  'vout': '" \
               + str(self.vout) + "',  'amount': '" + str(self.amount) + "'}"

    def as_dict(self):
        return {
            "address" : self.to_address,
            "txid" : self.txid,
            "vout" : self.vout,
            "amount" : self.amount
        }