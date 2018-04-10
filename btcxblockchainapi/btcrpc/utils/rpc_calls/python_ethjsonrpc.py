from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.rpc_calls.rpc_call import RPCCall
from btcrpc.utils.chain_enum import ChainEnum
from btcrpc.utils.address_encoding_flag import AddressEncodingFlag
from btcrpc.utils.constant_values import Constants
from btcrpc.view.models.transaction_fee_info import TransactionFeeInfo
import json
import socket, errno
from web3 import Web3, HTTPProvider

from btcrpc.utils.log import *

log = get_log("PythonBitcoinRpc Call:")


class PythonEthJsonRpc(RPCCall):
    def __init__(self, wallet, currency):
        yml_config_reader = ConfigFileReader()
        url = yml_config_reader.get_rpc_server(currency=currency, wallet=wallet)
        w3 = Web3(HTTPProvider(url))
        self.access = w3

    def amount_received_by_address(self, address="", confirms=0):
        raise NotImplementedError

    def do_getinfo(self):
        raise NotImplementedError

    def do_get_new_address(self, wallet):
        yml_config_reader = ConfigFileReader()
        key_encrypt_pass = yml_config_reader.get_private_key_encryption_password(
            currency=Constants.Currencies.ETHEREUM,
            wallet=wallet)
        address = self.access.personal.newAccount(key_encrypt_pass)
        return address

    def do_set_account(self, address, account):
        return True

    def do_get_transaction(self, txid):
        return self.access.eth.getTransaction(txid)

    def do_get_transaction_details(self, transaction_fee_info):
        transaction_info = self.do_get_transaction(transaction_fee_info.txid)
        to_address = transaction_info['to']
        amount = self.access.fromWei(abs(transaction_info['value']), "ether")
        return {
            "txid": transaction_fee_info.txid,
            "fee": transaction_fee_info.fee,
            "details": [
                {
                    "address": to_address,
                    "txid": transaction_fee_info.txid,
                    "vout": 0,
                    "amount": amount
                }
            ]
        }


    # def do_get_transactions_info(self, transactions):
    #     for transaction in transactions:
    #         txids = transaction["txids"]
    #         for txid in txids:
    #             transaction_info = self.do_get_transaction(txid)

    def do_get_fees_of_transactions(self, txids):
        txids_with_fee = []
        for txid in txids:
            transaction_info = self.do_get_transaction(txid)
            gas_amount = transaction_info['gas']
            gas_price = transaction_info['gasPrice']
            transactionFeeInWei = gas_amount * gas_price
            transactionFeeInEther = self.access.fromWei(transactionFeeInWei, "ether")
            txid_with_fee = TransactionFeeInfo(txid, transactionFeeInEther)
            txids_with_fee.append(txid_with_fee)
        return txids_with_fee

    def do_list_transactions(self, account, count=10, from_index=0):
        raise NotImplementedError

    def do_validate_address(self, address=""):

        is_valid_address = self.access.isAddress(address)
        if not is_valid_address:
            return {'isvalid': is_valid_address, 'ismine': False}

        # Since the address sent in might not be in checksum format, we convert it. Note: self.access.eth.accounts always
        # returns the accounts in checksum format. The toChecksumAddress also throws an exception if the address is not
        # valid hex format, therefore we check if it is valid before passing it to the toChecksumAddress function.
        check_sum_address = self.access.toChecksumAddress(address)
        wallet_account = \
            next((account for account in self.access.eth.accounts if account == self.access.toChecksumAddress(check_sum_address)),
                 None)
        address_is_mine = wallet_account is not None
        return {'isvalid': is_valid_address, 'ismine': address_is_mine}

    def encode_address(self, address, encoding_flag=AddressEncodingFlag.NO_SPECIFIC_ENCODING):
        print(encoding_flag)
        if encoding_flag == AddressEncodingFlag.ETHEREUM_CHECKSUM_ADDRESS:
            if self.access.isAddress(address):
                return self.access.toChecksumAddress(address)
            else:
                return address
        else:
            return address

    def list_transactions(self, account="", count=10, from_index=0):
        raise NotImplementedError

    def send_from(self, from_account="", to_address="", amount=0, minconf=1):
        raise NotImplementedError

    def get_blockchain_info(self):
        raise NotImplementedError

    def get_received_amount_by_account(self, account="", minconf=1):
        raise NotImplementedError

    def get_balance(self, account="", minconf=1):
        raise NotImplementedError

    def get_wallet_balance(self):
        accounts = self.access.eth.accounts
        account_balances = map(lambda account: self.access.fromWei(self.access.eth.getBalance(account), "ether"),
                               accounts)
        return sum(account_balances)

    def get_chain(self):
        try:
            network_id_string = self.access.net.version
            network_id_int = int(network_id_string)
            if network_id_int == 1:
                return ChainEnum.MAIN
            elif network_id_int == 0 \
                or network_id_int == 2 \
                or network_id_int == 3 \
                or network_id_int == 4 \
                or network_id_int == 42 \
                or network_id_int == 77:
                return ChainEnum.TEST_NET
            elif network_id_int == 1999:
                return ChainEnum.REGTEST
            else:
                return ChainEnum.UNKNOWN
        except ValueError:
            return ChainEnum.UNKNOWN

    def move(self, from_account="", to_account="", amount=0, minconf=1):
        raise NotImplementedError

    def list_accounts(self, confirmations=1):
        return self.access.eth.accounts

    def list_received_by_address(self, confirmations=1, include_empty=False):
        raise NotImplementedError

    def get_addresses_by_account(self, account):
        raise NotImplementedError

    def set_tx_fee(self, amount):
        # Since we want to use the fee suggested by the node software, we don't make a RPC call to manually set the fee.
        return False

    def send_to_address(self, address, amount, subtractfeefromamount=True, from_wallet=''):
        check_sum_address = self.access.toChecksumAddress(address)
        amount_left_to_send = self.access.toWei(amount, "ether")
        transaction_objects_list = []
        for account in self.access.eth.accounts:
            #NOTE TO BE REMOVED: ONLY FOR TESTING
            # if account == self.access.eth.accounts[0]:
            #     continue
            sender = account
            receiver = check_sum_address
            balance = self.access.eth.getBalance(sender)
            gas_price = self.access.eth.gasPrice
            transaction_object = {
                'from': sender,
                'to': receiver,
                'gasPrice': gas_price,
            }
            gas_amount = self.access.eth.estimateGas(transaction_object)
            transaction_object['gas'] = gas_amount
            transactionFee = gas_amount * gas_price

            if balance < transactionFee: #Theres either no balance to send or, only balance is lower than the transactionfee
                continue

            if balance < amount_left_to_send:
                transactionValue = balance - transactionFee
            else:
                if subtractfeefromamount:
                    transactionValue = amount_left_to_send - transactionFee
                elif amount_left_to_send + transactionFee > balance:
                    transactionValue = balance - transactionFee
                else:
                    transactionValue = amount_left_to_send

            transaction_object['value'] = transactionValue
            transaction_objects_list.append(transaction_object)
            amount_left_to_send = amount_left_to_send - transactionValue
            if subtractfeefromamount:
                amount_left_to_send = amount_left_to_send - transactionFee
            if amount_left_to_send <= 0:
                break

        # If this if case is hit, there is not enough funds in the wallet to send the entire amount to the address
        if amount_left_to_send > 0:
            raise JSONRPCException(
                "There are not enough funds in the wallet: "
                + from_wallet +
                " to fund the transaction of the amount: "
                + str(amount) +
                " To address: "
                + address
            )

        # We seperate the actual send of funds from the calculation and creation of the transactions, to make sure that
        # we don't run into a situation where there's only funds to partially fund the transaction. If that would happen,
        # It could potentially lead to that only of the percentage offunds was sent to the address, which would make the
        # situation tricky, as we would then need to have error handling to send the rest of the funds later.
        txids = []
        for trans_object in transaction_objects_list:
            yml_config_reader = ConfigFileReader()
            key_encrypt_pass = yml_config_reader.get_private_key_encryption_password(
                currency=Constants.Currencies.ETHEREUM,
                wallet=from_wallet)
            self.access.personal.unlockAccount(sender, key_encrypt_pass)
            txid = self.access.eth.sendTransaction(trans_object)
            self.access.personal.lockAccount(sender)
            txids.append(txid.hex())
            #self.access.eth.sendTransaction(transactionObject, callback_function)

        return txids

    # amount is type of dictionary
    def send_many(self, from_account="", minconf=1, from_wallet='', **amounts):
        transactions_succeeded = True
        transactions = []
        send_amount_dict = amounts['amounts']
        for to_address, amount in send_amount_dict.items():
            try:
                txids = self.send_to_address(
                    address=to_address,
                    amount=amount,
                    subtractfeefromamount=False,
                    from_wallet=from_wallet
                )
                transaction = self.generate_send_many_response(
                    txids,
                    "ok",
                    "Transfer is done"
                )
                transactions.append(transaction)
            except JSONRPCException as j_ex:
                transactions_succeeded = False
                transaction = self.generate_send_many_response(
                    [],
                    "fail",
                    "RPC error. Message from rpc client: " + j_ex.message
                )
                transactions.append(transaction)
            except BaseException as ex:
                transactions_succeeded = False
                transaction = self.generate_send_many_response(
                    [],
                    "fail",
                    "Base exception error. Error message: " + str(ex)
                )
                transactions.append(transaction)

        return transactions_succeeded, transactions
