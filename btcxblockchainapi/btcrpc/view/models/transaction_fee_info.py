from btcrpc.utils import constantutil

class TransactionFeeInfo(object):
    def __init__(self, txid, fee):
        self.txid = constantutil.not_none(txid)
        self.fee = constantutil.not_none(fee)

    def __str__(self):
        return "{ Txid: " + self.txid + ", Fee: " + str(self.fee) + " }"

    def __repr__(self):
        return "{ Txid: " + self.txid + ", Fee: " + str(self.fee) + " }"