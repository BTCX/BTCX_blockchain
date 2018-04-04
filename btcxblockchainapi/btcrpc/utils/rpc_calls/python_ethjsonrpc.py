from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.rpc_calls.rpc_call import RPCCall
from btcrpc.utils.chain_enum import ChainEnum
import json
import socket, errno
from web3 import Web3, HTTPProvider

from btcrpc.utils.log import *

log = get_log("PythonBitcoinRpc Call:")


class PythonEthJsonRpc(RPCCall):
    def __init__(self, wallet, currency):
        yml_config_reader = ConfigFileReader()
        url = yml_config_reader.get_rpc_server(currency=currency, wallet=wallet)
        print(url)
        w3 = Web3(HTTPProvider(url))
        print(w3.eth.blockNumber)

        self.access = w3

    def do_getinfo(self):
        return self.access.getinfo()

    def do_get_new_address(self):
        return self.access.getnewaddress()

    def do_set_account(self, address, account):
        return self.access.setaccount(address, account)

    def do_get_transaction(self, txid):
        try:
            return self.access.gettransaction(txid)
        except RuntimeError:
            # return simplejson.dumps ({u'error' : u'txid is not valid'})
            return None

    def do_list_transactions(self, account, count=10, from_index=0):
        try:
            return self.access.listtransactions(account, count, from_index)
        except RuntimeError:
            print("calling failure")

        def do_get_transaction(self, tx_id):
            try:
                return self.access.gettransaction(tx_id)
            except RuntimeError:
                # return simplejson.dumps ({u'error' : u'txid is not valid'})
                return None

    def amount_received_by_address(self, address="", confirms=0):
        return self.access.getreceivedbyaddress(address, confirms)

    def do_validate_address(self, address=""):
        return self.access.validateaddress(address)

    def list_transactions(self, account="", count=10, from_index=0):
        return self.access.listtransactions(account, count, from_index)

    def send_from(self, from_account="", to_address="", amount=0, minconf=1):
        return self.access.sendfrom(from_account, to_address, amount, minconf)

    def get_blockchain_info(self):
        return self.access.getblockchaininfo()

    def get_received_amount_by_account(self, account="", minconf=1):
        return self.access.getreceivedbyaccount(account, minconf)

    def get_balance(self, account="", minconf=1):
        return self.access.getbalance(account, minconf)

    def get_wallet_balance(self):
        accounts = self.access.eth.accounts
        account_balances = map(lambda account: self.access.fromWei(self.access.eth.getBalance(account), "ether"), accounts)
        return sum(account_balances)

    def get_chain(self):
        try:
            network_id_string = self.access.net.version
            network_id_int = int(network_id_string)
            if network_id_int == 1:
                return ChainEnum.MAIN
            elif network_id_int == 0 \
                or network_id_int == 2\
                or network_id_int == 3\
                or network_id_int == 4\
                or network_id_int == 42\
                or network_id_int == 77:
                return ChainEnum.TEST_NET
            elif network_id_int == 1999:
                return ChainEnum.REGTEST
            else:
                return ChainEnum.UNKNOWN
        except ValueError:
            return ChainEnum.UNKNOWN

    def move(self, from_account="", to_account="", amount=0, minconf=1):
        return self.access.move(from_account, to_account, amount, minconf)

    def list_accounts(self, confirmations=1):
        return self.access.listaccounts(confirmations)

    def list_received_by_address(self, confirmations=1, include_empty=False):
        return self.access.listreceivedbyaddress(confirmations, include_empty)

    def get_addresses_by_account(self, account):
        return self.access.getaddressesbyaccount(account)

    def set_tx_fee(self, amount):
        return self.access.settxfee(amount)

    def send_to_address(self, address, amount, subtractfeefromamount=True):
        return self.access.sendtoaddress(address, amount, "", "", subtractfeefromamount)

    # amount is type of dictionary
    def send_many(self, from_account="", minconf=1, **amounts):
        log.info("From account: %s", from_account)
        log.info("To accounts: %s", json.dumps(amounts))
        amounts_string = json.dumps(amounts['amounts'])
        amounts_object = json.loads(amounts_string)
        try:
            return True, self.access.sendmany(from_account, amounts_object, minconf)
            return True, self.access.sendmany(from_account, amounts_object, minconf)
        except JSONRPCException as ex:
            return False, ex
        except socket.error as e:
            return False, e
