from bitcoinrpc.authproxy import AuthServiceProxy
from btcxblockchainapi.servers_settings import BTC_RPC_SERVER

access = AuthServiceProxy(BTC_RPC_SERVER)


class BTCRPCCall(object):

    def __init__(self):
        pass

    @staticmethod
    def do_getinfo(self):
        return access.getinfo()

    @staticmethod
    def do_get_new_address(self):
        return access.getnewaddress();
    @staticmethod
    def do_set_account(self, address, account):
        return access.setaccount(address, account)

    @staticmethod
    def do_get_transaction(self, txid):
        try:
            return access.gettransaction(txid)
        except:
            #return simplejson.dumps ({u'error' : u'txid is not valid'})
            return None

    @staticmethod
    def do_list_transactions(self, account, count=10, from_index=0):
        try:
            return access.listtransactions(account, count, from_index)
        except:
            print "calling failure"

    @staticmethod
    def amount_received_by_address(self, address="", confirms=0):
        return access.getreceivedbyaddress(address, confirms);
        
    @staticmethod
    def do_validate_address(self, address=""):
        return access.validateaddress(address)

    @staticmethod
    def list_transactions(account="", count=10, from_index=0):
        return access.listtransactions(account, count, from_index)
