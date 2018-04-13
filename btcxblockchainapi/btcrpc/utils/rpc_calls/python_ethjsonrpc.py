from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.rpc_calls.rpc_call import RPCCall
from btcrpc.utils.chain_enum import ChainEnum
from btcrpc.utils.address_encoding_flag import AddressEncodingFlag
from btcrpc.utils.constant_values import Constants
from btcrpc.view.models.transaction_fee_info import TransactionFeeInfo
from btcrpc.view.models.get_account_iterator import GetAccountIterator
from btcrpc.view.models.transaction_object import TransactionObject
from btcrpc.view.models.transaction_details import TransactionDetails
from btcrpc.utils.log import get_log, log_info, log_error
import json
import socket, errno
from web3 import Web3, HTTPProvider

log = get_log("PythonEthereumRpc Call:")


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

    def do_get_transaction_details(self, transaction_object):
        transaction_info = self.do_get_transaction(transaction_object.txid)
        to_address = transaction_info['to']
        amount = self.access.fromWei(abs(transaction_info['value']), "ether")
        details = TransactionDetails(to_address=to_address, txid=transaction_object.txid, vout=0, amount=amount)
        return TransactionObject(transaction_object.txid, fee = transaction_object.fee, details = [details])

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
        addresses_and_amounts_dict = {}
        addresses_and_amounts_dict[address] = amount
        return self.send_to_addresses(addresses_and_amounts_dict, subtractfeefromamount, from_wallet)

    def send_to_addresses(self, addresses_and_amounts = {}, subtractfeefromamount=True, from_wallet=''):
        # The reason we define the account list before the addresses_and_amounts.items() loop is because the
        # eth.sendTransaction(trans_object) does not immediately update the account balance for an eth.getBalance(sender)
        # request. It is only updated once a transaction from the account is confirmed in a block.
        # Therefore if we made a loop over all accounts inside the addresses_and_amounts.items() loop that restarts with
        # every step in the addresses_and_amounts.items() loop, the balances for the accounts might not be updated that
        # we have just sent transactions from. The loop would then use the same accounts again to send new transactions,
        # leading to double spend transactions where only one transaction would be accepted.
        account_iterator = GetAccountIterator(self.access.eth.accounts)
        txids = []
        try:
            for to_address, amount in addresses_and_amounts.items():
                check_sum_address = self.access.toChecksumAddress(to_address)
                amount_left_to_send = self.access.toWei(amount, "ether")
                transaction_objects_list = []

                # Could likely be replaced by making the GetAccountIterator class ovveride the ___iter___ function to and use
                # the get_next_suitable_account function to set the item returned
                account = account_iterator.get_next_suitable_account()
                while account is not None:
                    #NOTE TO BE REMOVED: ONLY FOR TESTING
                    if account == self.access.eth.accounts[0]:
                        account_iterator.increase_account_index()
                        account = account_iterator.get_next_suitable_account()
                        continue

                    sender = account
                    receiver = check_sum_address
                    balance = account_iterator.get_balance_of_account(sender) \
                        if account_iterator.has_balance_set_for_account(sender) \
                        else self.access.eth.getBalance(sender)
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
                        account_iterator.increase_account_index()
                        account = account_iterator.get_next_suitable_account()
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

                    new_account_balance = balance - transactionValue - transactionFee
                    # Ensures that the account_iterator has the new balance of the account, even though eth.getBalance will
                    # not have updated.
                    account_iterator.set_balance_of_account(sender, new_account_balance)

                    if subtractfeefromamount:
                        amount_left_to_send = amount_left_to_send - transactionFee
                    if amount_left_to_send <= 0:
                        break
                    account = account_iterator.get_next_suitable_account()

                # If this if case is hit, there is not enough funds in the wallet to send the entire amount to the address
                if amount_left_to_send > 0:
                    exception_string = "There are not enough funds in the wallet: " + from_wallet + " to fund the transaction "\
                                        "of the amount: " + str(amount) + " To address: " + to_address
                    raise JSONRPCException({'code': -343, 'message': exception_string})

                # We seperate the actual send of funds from the calculation and creation of the transactions, to make sure that
                # we don't run into a situation where there's only funds to partially fund the transaction. If that would happen,
                # It could potentially lead to that only of the percentage offunds was sent to the address, which would make the
                # situation tricky, as we would then need to have error handling to send the rest of the funds later.
                for trans_object in transaction_objects_list:
                    yml_config_reader = ConfigFileReader()
                    key_encrypt_pass = yml_config_reader.get_private_key_encryption_password(
                        currency=Constants.Currencies.ETHEREUM,
                        wallet=from_wallet)
                    sender = trans_object['from']
                    self.access.personal.unlockAccount(sender, key_encrypt_pass)
                    txidBytes = self.access.eth.sendTransaction(trans_object)
                    self.access.personal.lockAccount(sender)
                    txid = txidBytes.hex()
                    propagated_transaction = self.access.eth.getTransaction(txid)
                    if propagated_transaction is not None:
                        txids.append(txid)
                    else:
                        # NOTE: If this case executes, it means that sendTransaction never propagated the transaction to the network.
                        # This can unfortunatly happen sometimes, for some strange reason.
                        error_message = "The eth.sendTransaction generated the txid " + txid + \
                                        " even though the transaction was never popagted to the network. " \
                                        "Transaction object to send"
                        log_error(log, error_message, trans_object)

        except JSONRPCException as j_ex:
            error_message = "RPC error. Message from rpc client: " + str(j_ex)
            log_error(log, error_message, j_ex)
        except BaseException as ex:
            error_message = "Base exception error. Error message: " + str(ex)
            log_error(log, error_message, ex)

        # We want to make sure that we return any txids that actually succeeded, even if an exception was raised,
        # therefore we never return anything and just log the exception from the exception clauses,
        # and always return the txids.
        return txids


    def send_many(self, from_account="", minconf=1, from_wallet='', **amounts):
        send_amount_dict = amounts['amounts']
        txids = self.send_to_addresses(
            addresses_and_amounts = send_amount_dict,
            subtractfeefromamount=False,
            from_wallet=from_wallet)
        any_transaction_succeeded = len(txids) > 0
        return any_transaction_succeeded, txids
