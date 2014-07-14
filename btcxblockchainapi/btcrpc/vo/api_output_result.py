from btcrpc.utils.constantutil import constant


STATUS_RECEIVED = "received"
STATUS_PENDING = "pending"


class AddressReceiveOutputAttributeConst(object):

    @constant
    def APIKEY():
        return "apikey"

    @constant
    def CURRENCY():
        return "currency"

    @constant
    def TEST():
        return "test"

    @constant
    def AMOUNT():
        return "amount"

    @constant
    def TXID():
        return "txid"

    @constant
    def ADDRESS():
        return "address"

    @constant
    def TIMERECEIVED():
        return "timereceived"

    @constant
    def BLOCKTIME():
        return "blocktime"

    @constant
    def STATUS():
        return "status"

    @constant
    def CONFIRMATIONS():
        return "confirmations"
   
    @constant
    def DETAILS():
        return "details"

    @constant
    def MINCONF():
        return "confirms"
