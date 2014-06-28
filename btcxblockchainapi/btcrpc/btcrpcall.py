from bitcoinrpc.authproxy import AuthServiceProxy


btcRPCServer = "http://Ulysseys:8NzhGAbEXoJahLkPpNzmLxHqvQusgYVJWWx1J83y95gQ@127.0.0.1:18332" 
access = AuthServiceProxy(btcRPCServer)

class BTCRPCall(object):

    def __init__(self):
        pass

    def do_getinfo(self):
        return access.getinfo()

    def do_get_new_address(self):
        return access.getnewaddress();

    def do_list_transactions():
        return access.listtransactions();

    def do_received_by_address(address = "", minconf = 0):
        return access.getreceivedbyaddress(address, minconf);
