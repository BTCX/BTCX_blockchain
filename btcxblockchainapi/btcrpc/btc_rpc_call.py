from bitcoinrpc.authproxy import AuthServiceProxy
from btcxblockchainapi.servers_settings import BTC_RPC_SERVER

access = AuthServiceProxy(BTC_RPC_SERVER)


class BTCRPCCall(object):

    def __init__(self):
        pass

    @staticmethod
    def do_getinfo():
        return access.getinfo()

    @staticmethod
    def do_get_new_address():
        return access.getnewaddress();

    @staticmethod
    def do_set_account(address, account):
        return access.setaccount(address, account)

    @staticmethod
    def do_get_transaction(txid):
        try:
            return access.gettransaction(txid)
        except:
            #return simplejson.dumps ({u'error' : u'txid is not valid'})
            return None

    @staticmethod
    def do_list_transactions(account, count=10, from_index=0):
        try:
            return access.listtransactions(account, count, from_index)
        except:
            print "calling failure"

    @staticmethod
    def amount_received_by_address(address="", confirms=0):
        return access.getreceivedbyaddress(address, confirms);
        
    @staticmethod
    def do_validate_address(address=""):
        return access.validateaddress(address)

    @staticmethod
    def list_transactions(account="", count=10, from_index=0):
        return access.listtransactions(account, count, from_index)

    @staticmethod
    def send_from(from_account="", to_address="", amount=0, minconf=1):
        return access.sendfrom(from_account, to_address, amount, minconf)

    @staticmethod
    def get_received_amount_by_account(account="", minconf=1):
        return access.getreceivedbyaccount(account, minconf)

    @staticmethod
    def get_balance(account="", minconf=1):
        return access.getbalance(account, minconf)