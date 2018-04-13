from btcrpc.utils import constantutil

class TransactionObject(object):
    def __init__(self, txid, fee = 0, details = []):
        self.txid = constantutil.not_none(txid)
        self.fee = fee
        self.details = details

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def __dict__(self):
        return {
            "txid" : self.txid,
            "fee" : self.fee,
            "details" : self.details
        }