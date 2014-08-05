from btcrpc.utils.constantutil import constant


STATUS_COMPLETED = "completed"
STATUS_PENDING = "pending"
STATUS_FAILED = "failed"


class AddressReceiveOutputAttributeConst(object):

    @constant
    def APIKEY(self):
        return "apikey"

    @constant
    def CURRENCY(self):
        return "currency"

    @constant
    def TEST(self):
        return "test"

    @constant
    def AMOUNT(self):
        return "amount"

    @constant
    def TXID(self):
        return "txid"

    @constant
    def ADDRESS(self):
        return "address"

    @constant
    def TIMERECEIVED(self):
        return "timereceived"

    @constant
    def BLOCKTIME(self):
        return "blocktime"

    @constant
    def STATUS(self):
        return "status"

    @constant
    def CONFIRMATIONS(self):
        return "confirmations"
   
    @constant
    def DETAILS(self):
        return "details"

    @constant
    def MINCONF(self):
        return "confirms"

    @constant
    def QUANTITY(self):
        return "quantity"
