from btcrpc.utils.constantutil import not_none

class TransactionFeeInfo(object):
    def __init__(self, txid, fee):
        self.txid = not_none(txid)
        self.fee = not_none(fee)

    def __str__(self):
        return "{ Txid: " + self.txid + ". Fee: " + str(self.fee) + " }"

    def __repr__(self):
        return "{ Txid: " + self.txid + ". Fee: " + str(self.fee) + " }"