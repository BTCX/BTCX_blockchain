from bitcoinrpc.authproxy import AuthServiceProxy
from btcxblockchainapi.servers_settings import Digital_Crypto_Currency_Server


class BTCRPCCall(object):

    def __init__(self, wallet="receive", currency="btc", test=True):
        btc_rpc_servers = Digital_Crypto_Currency_Server[currency]
        btc_rpc_server = btc_rpc_servers[wallet]
        if btc_rpc_server["test"] == test:
            self.access = AuthServiceProxy(btc_rpc_server["host"])
        else:
            print "there is no a proper wallet "

    def do_getinfo(self):
        return self.access.getinfo()

    def do_get_new_address(self):
        return self.access.getnewaddress();

    def do_set_account(self, address, account):
        return self.access.setaccount(address, account)

    def do_get_transaction(self, txid):
        try:
            return self.access.gettransaction(txid)
        except RuntimeError:
            #return simplejson.dumps ({u'error' : u'txid is not valid'})
            return None

    def do_list_transactions(self, account, count=10, from_index=0):
        try:
            return self.access.listtransactions(account, count, from_index)
        except RuntimeError:
            print "calling failure"

    def amount_received_by_address(self, address="", confirms=0):
        return self.access.getreceivedbyaddress(address, confirms);

    def do_validate_address(self, address=""):
        return self.access.validateaddress(address)

    def list_transactions(self, account="", count=10, from_index=0):
        return self.access.listtransactions(account, count, from_index)

    def send_from(self, from_account="", to_address="", amount=0, minconf=1):
        return self.access.sendfrom(from_account, to_address, amount, minconf)

    def get_received_amount_by_account(self, account="", minconf=1):
        return self.access.getreceivedbyaccount(account, minconf)

    def get_balance(self, account="", minconf=1):
        return self.access.getbalance(account, minconf)