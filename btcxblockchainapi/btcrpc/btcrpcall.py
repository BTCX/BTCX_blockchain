from bitcoinrpc.authproxy import AuthServiceProxy
import simplejson

btcRPCServer = "http://Ulysseys:8NzhGAbEXoJahLkPpNzmLxHqvQusgYVJWWx1J83y95gQ@127.0.0.1:18332" 
ltcRPCServer = ""
dogecoinRPCServer = ""

access = AuthServiceProxy(btcRPCServer)

class BTCRPCall(object):

    def __init__(self):
        pass

    def do_getinfo(self):
        return access.getinfo()

    def do_get_new_address(self):
        return access.getnewaddress();

    def do_set_account(self,address, account):
        print access.setaccount(address, account)
    
    def do_get_transaction(self,txid):
        try:
            return access.gettransaction(txid)
        except:
            #return simplejson.dumps ({u'error' : u'txid is not valid'})
            return None

    def do_list_transactions(self, account, count = 10, from_index = 0):
        try:
            return access.listtransactions(account, count, from_index)
        except:
            print "calling failure"
    
    def do_received_by_address(self, address = "", confirms = 0):
        return access.getreceivedbyaddress(address, confirms);
        
    
