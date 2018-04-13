from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.rpc_calls.rpc_call import RPCCall
from btcrpc.utils.chain_enum import ChainEnum
from btcrpc.utils.address_encoding_flag import AddressEncodingFlag
from btcrpc.view.models.transaction_fee_info import TransactionFeeInfo
from btcrpc.view.models.transaction_object import TransactionObject
from btcrpc.view.models.transaction_details import TransactionDetails
import json
import socket, errno

from btcrpc.utils.log import get_log, log_info, log_error

log = get_log("PythonBitcoinRpc Call:")


class PythonBitcoinRpc(RPCCall):
    def __init__(self, wallet, currency):
        yml_config_reader = ConfigFileReader()
        url = yml_config_reader.get_rpc_server(currency=currency, wallet=wallet)
        self.access = AuthServiceProxy(url)

    def amount_received_by_address(self, address="", confirms=0):
        return self.access.getreceivedbyaddress(address, confirms)

    def do_getinfo(self):
        return self.access.getinfo()

    def do_get_new_address(self, wallet):
        return self.access.getnewaddress()

    def do_set_account(self, address, account):
        return self.access.setaccount(address, account)

    def do_get_fees_of_transactions(self, txids):
        txids_with_fee = []
        for txid in txids:
            transaction_info = self.do_get_transaction(txid)
            fee = abs(transaction_info['fee'])
            txid_with_fee = TransactionFeeInfo(txid, fee)
            txids_with_fee.append(txid_with_fee)
        return txids_with_fee

    def do_get_transaction(self, txid):
        try:
            return self.access.gettransaction(txid)
        except RuntimeError:
            # return simplejson.dumps ({u'error' : u'txid is not valid'})
            return None


    def do_get_transaction_details(self, transaction_object):
        transaction_info = self.do_get_transaction(transaction_object.txid)
        details = transaction_info["details"]
        details_list = []
        for transactionDetail in details:
            if (transactionDetail['category'] == 'send'):
                details_list.append(self.get_output_details(transactionDetail, transaction_object.txid))
        return  TransactionObject(transaction_object.txid, fee = transaction_object.fee, details = details_list)


    def get_output_details(self, transaction_detail, txid):
        #log_info(log, "Transaction detail for txid " + txid, transaction_detail)
        return TransactionDetails(to_address=transaction_detail['address'],
                                  txid=txid,
                                  vout=transaction_detail['vout'],
                                  amount=abs(transaction_detail['amount']))

    def do_list_transactions(self, account, count=10, from_index=0):
        try:
            return self.access.listtransactions(account, count, from_index)
        except RuntimeError:
            print("calling failure")

    def do_validate_address(self, address=""):
        return self.access.validateaddress(address)

    def encode_address(self, address, encoding_flag=AddressEncodingFlag.NO_SPECIFIC_ENCODING):
        return address

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
        return self.access.getbalance()

    def get_chain(self):
        blockchain_info = self.get_blockchain_info()
        if blockchain_info["chain"] == "main":
            return ChainEnum.MAIN
        elif blockchain_info["chain"] == "test":
            return ChainEnum.TEST_NET
        elif blockchain_info["chain"] == "regtest":
            return ChainEnum.REGTEST
        else:
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

    def send_to_address(self, address, amount, subtractfeefromamount=True, from_wallet=''):
        return [self.access.sendtoaddress(address, amount, "", "", subtractfeefromamount)]

    # amount is type of dictionary
    def send_many(self, from_account="", minconf=1, from_wallet="", **amounts):
        log.info("From account: %s", from_account)
        log.info("To accounts: %s", json.dumps(amounts))
        amounts_string = json.dumps(amounts['amounts'])
        amounts_object = json.loads(amounts_string)
        try:
            txid = self.access.sendmany(from_account, amounts_object, minconf)
            log_info(log, "Send many request succeeded with txid", txid)
            return True, [txid]
        except JSONRPCException as j_ex:
            error_message = "RPC error. Message from rpc client: " + str(j_ex)
            log_error(log, error_message, j_ex)
            return False, []
        except BaseException as ex:
            error_message = "Base exception error. Error message: " + str(ex)
            log_error(log, error_message, ex)
            return False, []
