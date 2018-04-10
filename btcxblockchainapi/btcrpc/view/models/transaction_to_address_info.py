from btcrpc.utils import constantutil

class TransactionToAddressInfo(object):
    def __init__(self, txids, status, message):
        self.txids = constantutil.not_none(txids)
        self.status = constantutil.not_none(status)
        self.message = constantutil.not_none(message)

    def get_properties_ingo_string(self):
        s = ","
        txids_string = s.join(self.txids)
        return "{ Txids: [" + txids_string +"], Status: " + self.status + ", Message: " + self.message + "}"

    def __str__(self):
        return self.get_properties_ingo_string()

    def __repr__(self):
        return self.get_properties_ingo_string()