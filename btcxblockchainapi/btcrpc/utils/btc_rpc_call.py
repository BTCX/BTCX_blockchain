from bitcoinrpc.authproxy import AuthServiceProxy
from btcrpc.utils.config_file_reader import ConfigFileReader


class BTCRPCCall(object):

    def __init__(self, wallet="receive", currency="btc"):
        yml_config_reader = ConfigFileReader()
        url = yml_config_reader.get_rpc_server(currency=currency, wallet=wallet)

        self.access = AuthServiceProxy(url)

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

    def move(self, from_account="", to_account="", minconf=1):
        return self.access.move(from_account, to_account, minconf)

    def list_accounts(self, confirmations=1):
        return self.access.listaccounts(confirmations)

    def list_received_by_address(self, confirmations=1, include_empty=False):
        return self.access.listreceivedbyaddress(confirmations, include_empty)