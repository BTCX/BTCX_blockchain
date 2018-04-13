from btcrpc.utils import constantutil

class TransactionObject(object):
    def __init__(self, txid, fee = 0, details = []):
        self.txid = constantutil.not_none(txid)
        self.fee = fee
        self.details = details

    def __str__(self):
        return self.get_self_str()

    def __repr__(self):
        return self.get_self_str()

    def get_self_str(self):
        details_string = "["
        for index, detail in enumerate(self.details):
            if index > 0:
                details_string += ", "
            details_string += str(detail)
        details_string += "]"
        return "{'txid': '" + self.txid + "', 'fee': '" + str(self.fee) + "',  'details': " + details_string + "}"

    def as_dict(self):
        details_dict_list = [detail.as_dict() for detail in self.details]
        return {
            "txid" : self.txid,
            "fee" : self.fee,
            "details" : details_dict_list
        }