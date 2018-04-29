from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.rpc_calls.rpc_call import RPCCall
from btcrpc.utils.chain_enum import ChainEnum
from btcrpc.utils.address_encoding_flag import AddressEncodingFlag
from btcrpc.utils.constant_values import Constants
from btcrpc.view.models.transaction_fee_info import TransactionFeeInfo
from btcrpc.view.models.transaction_object import TransactionObject
from btcrpc.view.models.transaction_details import TransactionDetails
from btcrpc.utils.log import get_log, log_info, log_error
import json
import socket, errno
from web3 import Web3, HTTPProvider
import requests
import time

log = get_log("PythonEthereumRpc Call:")


class PythonEthJsonRpc(RPCCall):
    def __init__(self, wallet, currency, endpoint_timer):
        yml_config_reader = ConfigFileReader()
        url = yml_config_reader.get_rpc_server(currency=currency, wallet=wallet)
        w3 = Web3(HTTPProvider(url))
        self.access = w3
        self.endpoint_timer = endpoint_timer

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

    def get_pending_transactions(self):
        return self.access.manager.request_blocking(
            "eth_pendingTransactions",
            []
        )

    def get_received_amount_by_account(self, account="", minconf=1):
        raise NotImplementedError

    def get_balance(self, account="", minconf=1):
        raise NotImplementedError

    def get_gasPrice(self):
        return self.access.eth.gasPrice

    def get_real_account_balance_in_wei(self, account):
        (pending_account_balance, confirmed_account_balance, pending_transactions) = \
            self.get_pending_and_confirmed_balance_in_wei_and_pending_transactions(account)
        return pending_account_balance

    def get_pending_and_confirmed_balance_in_wei_and_pending_transactions(self, account):
        account_as_checksum_address = self.access.toChecksumAddress(account)
        # confirmed_account_balance = self.access.fromWei(self.access.eth.getBalance(account), "ether")
        (confirmed_account_balance, pending_transactions) = \
            self.get_confirmed_balance_with_pending_transactions(account_as_checksum_address)
        pending_account_balance = confirmed_account_balance
        #retrieves only the pending transactions sent by the wallet

        for pending_transaction in pending_transactions:
            if account_as_checksum_address == self.access.toChecksumAddress(pending_transaction['from']):
                #All values in the transaction are in hex, so we need to convert them to ints.
                pending_transaction_full_amount = self.get_full_transaction_amount_in_wei(pending_transaction)
                pending_account_balance -= pending_transaction_full_amount
        return (pending_account_balance, confirmed_account_balance, pending_transactions)

    def get_full_transaction_amount_in_wei(self, transaction_dict):
        (transaction_value, transaction_gas_price, transaction_gas_amount) = \
            self.get_transaction_amounts_in_wei(transaction_dict)
        transaction_fee = transaction_gas_amount * transaction_gas_price
        return transaction_value + transaction_fee

    def get_transaction_amounts_in_wei(self, transaction_dict):
        transaction_value = int(str(transaction_dict['value']), 0)
        transaction_gas_price = int(str(transaction_dict['gasPrice']), 0)
        transaction_gas_amount = int(str(transaction_dict['gas']), 0)
        return (transaction_value, transaction_gas_price, transaction_gas_amount)

    '''This function makes sure that the we get the real confirmed account balance with the corresponding pending 
    transactions. If we did not do the equal checks that is in this function, and just did first the eth.getBalance
    followed by the get_pending_transaction call and jsut returned those, we could end up with a situation where
    the pending transaction list could have changed between the two calls, and therefore returning an incorrect balance 
    value'''
    def get_confirmed_balance_with_pending_transactions(self, account):

        confirmed_account_balance_first_check = self.access.eth.getBalance(account)
        pending_transactions_first_check = self.get_pending_transactions()
        confirmed_account_balance_second_check = self.access.eth.getBalance(account)
        pending_transactions_second_check = self.get_pending_transactions()
        # We need to do this second check of the pending transactions also, because theoretically between the first
        # pending transaction check and sencond balance check there could have been pending transactions confirmed, and
        # also new ones that entered the pending pool that confirmed, that EXACTLY set the balance to the same balance
        # as the first check for the secnond balance check

        if confirmed_account_balance_first_check != confirmed_account_balance_second_check:
            return self.get_confirmed_balance_with_pending_transactions(account)
        elif pending_transactions_first_check != pending_transactions_second_check:
            return self.get_confirmed_balance_with_pending_transactions(account)
        else:
            #The balance and pending transactions are correct
            return (confirmed_account_balance_first_check, pending_transactions_first_check)


    def get_wallet_has_queued_transactions(self):
        accounts = self.access.eth.accounts
        txpool_status = self.access.txpool.status
        number_of_queued_transactions = int(txpool_status['queued'], 0)
        if number_of_queued_transactions == 0:
            return False
        queued_transactions = self.access.txpool.content['queued']
        for account in accounts:
            for queued_transaction_account, account_queued_transactions in queued_transactions.items():
                if account == account:
                    return True
        return False
        # for pending_transaction_account, account_pending_transactions in pending_transactions.items():
        #     if account == pending_transaction_account:
        #         for nonce, transactions_for_nonce in account_pending_transactions.items():
        #             max_gas_price = 0
        #             max_priced_transaction_index = 0
        #             for transaction_index, transaction in enumerate(transactions_for_nonce):
        #                 transaction_gas_price = transaction['gasPrice']
        #                 if transaction_gas_price > max_gas_price:
        #                     max_gas_price = transaction_gas_price
        #                     max_priced_transaction_index = transaction_index
        #             max_priced_transaction = transactions_for_nonce[max_priced_transaction_index]
        #             max_priced_gas_amount = max_priced_transaction['gas']
        #             max_priced_transaction_transaction_value = max_priced_transaction['value']
        #             max_priced_transaction_fee = max_priced_gas_amount * max_gas_price
        #             amount_to_subtract_from_balance = self.access.fromWei(
        #                 max_priced_transaction_transaction_value + max_priced_transaction_fee,
        #                 "ether"
        #             )
        #             real_account_balance_with_pending_transactions -= amount_to_subtract_from_balance


    def get_wallet_balance(self):
        self.validate_that_geth_is_synced()
        accounts = self.access.eth.accounts
        account_balances = map(lambda account: self.access.fromWei(self.get_real_account_balance_in_wei(account), "ether"),
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
        txids = []
        try:
            self.call_func_and_validate_timeout(
                func=self.validate_that_geth_is_synced,
                log_message="Geth is synced"
            )
            account_start_index = 0
            for to_address, amount in addresses_and_amounts.items():
                check_sum_address = self.call_func_and_validate_timeout(
                    func = self.access.toChecksumAddress,
                    func_args = {"address":to_address},
                    log_message = "to_address is: " + to_address + ". Checksum address is"
                )
                amount_left_to_send = self.call_func_and_validate_timeout(
                    func = self.access.toWei,
                    func_args = {'number':amount, 'unit':"ether"},
                    log_message = "Amount left to send is"
                )
                transaction_objects_list = []

                # The [account_start_index:] ensures that we don't loop over accounts already determined to be empty.
                # This is only made to optimise the runtime of the loop, as if this was not done, we would loop over
                # The entire account list for every step in the addresses_and_amounts.items() loop
                account_list_with_empty_accounts_skipped = self.access.eth.accounts[account_start_index:]
                log_info(log, "None empty accounts to loop over ", account_list_with_empty_accounts_skipped)

                number_of_elements_skipped = account_start_index
                log_info(log, "Number of elements skipped ", number_of_elements_skipped)

                self.endpoint_timer.validate_is_within_timelimit()

                for index, account in enumerate(account_list_with_empty_accounts_skipped):

                    # Please note that we don't use index + number_of_elements_skipped + 1 as there can still be balance
                    # on the account of index, after the funds has been used for this specific transaction.
                    account_start_index = index + number_of_elements_skipped
                    log_info(log, "account_start_index ", account_start_index)

                    #NOTE TO BE REMOVED: ONLY FOR TESTING
                    # if account == self.access.eth.accounts[0]:
                    #     continue

                    sender = account
                    log_info(log, "Sender account ", sender)

                    receiver = check_sum_address

                    # NOTE!!! Make sure to use a balance that subtracts pending transactions (which
                    # get_real_account_balance_in_wei does), else this function will lead to double spend transactions.
                    # as the account list resets for every new transaction to send to.
                    balance = self.call_func_and_validate_timeout(
                        func = self.get_real_account_balance_in_wei,
                        func_args = {'account':sender},
                        log_message = "Real account balance of sender is"
                    )

                    gas_price = self.call_func_and_validate_timeout(
                        func = self.get_gasPrice,
                        log_message = "Gas price used is"
                    )

                    transaction_object = {
                        'from': sender,
                        'to': receiver,
                        'gasPrice': gas_price,
                    }
                    log_info(log, "Transaction object is", transaction_object)

                    gas_amount = self.call_func_and_validate_timeout(
                        func = self.access.eth.estimateGas,
                        func_args = {'transaction':transaction_object},
                        log_message = "The estimated gas amount for the transaction object is"
                    )

                    transaction_object['gas'] = gas_amount
                    transaction_fee = gas_amount * gas_price
                    log_info(log, "Transaction fee is", transaction_fee)

                    lower_balance_than_lowest_possible_send_amount = balance < transaction_fee
                    log_info(log, "lower_balance_than_lowest_possible_send_amount is",
                             lower_balance_than_lowest_possible_send_amount)

                    if lower_balance_than_lowest_possible_send_amount:
                        #Theres either no balance to send or, only balance is lower than the transactionfee
                        continue

                    balance_below_amount_to_send = balance < amount_left_to_send
                    log_info(log, "balance_below_amount_to_send is",
                             balance_below_amount_to_send)

                    if balance_below_amount_to_send:
                        transaction_value = balance - transaction_fee
                    else:
                        log_info(log, "subtractfeefromamount is",subtractfeefromamount)

                        balance_below_amount_plus_transaction_fee = amount_left_to_send + transaction_fee > balance
                        log_info(log, "balance_below_amount_plus_transaction_fee is",
                                 balance_below_amount_plus_transaction_fee)

                        if subtractfeefromamount:
                            transaction_value = amount_left_to_send - transaction_fee
                        elif balance_below_amount_plus_transaction_fee:
                            transaction_value = balance - transaction_fee
                        else:
                            transaction_value = amount_left_to_send

                    log_info(log, "transaction_value is", transaction_value)
                    transaction_object['value'] = transaction_value
                    log_info(log,"Transaction object after adding value is", transaction_object)

                    transaction_objects_list.append(transaction_object)
                    log_info(log, "transaction_objects_list after adding transaction object is", transaction_objects_list)

                    amount_left_to_send = amount_left_to_send - transaction_value
                    log_info(log, "amount left to send after subtracting transaction value is", amount_left_to_send)

                    if subtractfeefromamount:
                        amount_left_to_send = amount_left_to_send - transaction_fee
                        log_info(log, "amount left to send after subtracting transaction FEE is", amount_left_to_send)
                    if amount_left_to_send <= 0:
                        log_info(log, "Amount left to send is 0 or below, breaking loop at account", account)
                        break

                # If this if case is hit, there is not enough funds in the wallet to send the entire amount to the address
                if amount_left_to_send > 0:
                    exception_string = "There are not enough funds in the wallet: " + from_wallet + " to fund the transaction "\
                                        "of the amount: " + str(amount) + " To address: " + to_address + ". Amount left " \
                                        "required is " + str(amount_left_to_send)
                    log_error(log, exception_string)
                    raise JSONRPCException({'code': -343, 'message': exception_string})

                self.call_void_func_and_validate_timeout(
                    func=self.validate_that_geth_is_synced,
                    log_message="Geth is synced"
                )

                # We seperate the actual send of funds from the calculation and creation of the transactions, to make sure that
                # we don't run into a situation where there's only funds to partially fund the transaction. If that would happen,
                # It could potentially lead to that only of the percentage offunds was sent to the address, which would make the
                # situation tricky, as we would then need to have error handling to send the rest of the funds later.
                log_info(log, "transaction_objects_list to send is", transaction_objects_list)
                for trans_object in transaction_objects_list:
                    log_info(log, "trans_object to send is is", trans_object)
                    yml_config_reader = ConfigFileReader()
                    key_encrypt_pass = yml_config_reader.get_private_key_encryption_password(
                        currency=Constants.Currencies.ETHEREUM,
                        wallet=from_wallet)
                    sender = trans_object['from']

                    unlocked = self.call_func_and_validate_timeout(
                        func = self.access.personal.unlockAccount,
                        func_args = {'account':sender, 'passphrase': key_encrypt_pass},
                        log_message = "Account " + sender +" is unlocked is"
                    )

                    (pending_b1, confirmed_b1, pending_txs1) = self.call_func_and_validate_timeout(
                        func = self.get_pending_and_confirmed_balance_in_wei_and_pending_transactions,
                        func_args = {'account':sender},
                        log_message = "Pending balance, confirmed balance and pending transactions is"
                    )

                    txid_bytes = self.access.eth.sendTransaction(trans_object)
                    # We want to ensure that we get the txid back within the timelimit, therefore we catch the timeout
                    # exception if thrown and return the information about the transaction we got. The calling function
                    # will have checks for timeouts within it, to ensure that the is timedout.
                    tx_information = None
                    try:
                        if txid_bytes is not None:
                            log_info(log, "txid_bytes is", txid_bytes)
                            #The txid returned by sendTransaction is of type hexBytes. To get the hex string, we run .hex()
                            txid = txid_bytes.hex()
                            log_info(log, "setting tx_information to", txid)
                            tx_information = txid
                        else:
                            # We don't check for timeouts in this case, as it is more important to fetch txids that might
                            # have been transmitted without the eth.sendTransaction returning it
                            log_error(log, "No txid was returned by send transaction for trans_object", trans_object)
                            (pending_b2, confirmed_b2, pending_txs2) = \
                                self.get_pending_and_confirmed_balance_in_wei_and_pending_transactions(sender)
                            log_info(
                                log,
                                "AFTER send. Pending balance, confirmed balance and pending transactions is",
                                (pending_b2, confirmed_b2, pending_txs2))
                            # The sendTransaction returned nothing. However ethereum sometimes still sends a transaction when
                            # even though sendTransaction returns nothing. We must check if there is a new txid added.
                            txid = self.handle_no_txid_returned_for_sendtransaction(
                                trans_object=trans_object,
                                pending_balance_before_sent=pending_b1,
                                pending_balance_after_sent=pending_b2,
                                pending_transactions_before_sent=pending_txs1,
                                pending_transactions_after_sent=pending_txs2
                            )
                            log_info(log, "The handle_no_txid_returned_for_sendtransaction call returned", txid)
                            log_info(log, "setting tx_information to", txid)
                            tx_information = txid

                        if tx_information is not None:
                            locked = self.call_func_and_validate_timeout(
                                func = self.access.personal.lockAccount,
                                func_args = {'account':sender},
                                log_message = "Account " + sender +" is locked is"
                            )

                            propagated_transaction = self.call_func_and_validate_timeout(
                                func = self.access.eth.getTransaction,
                                func_args = {'transaction_hash':txid},
                                log_message = "The propageted transaction of txid " + txid + " is"
                            )
                            if propagated_transaction is not None:
                                self.__append_to_list_and_log(
                                    list_to_append_to=txids,
                                    list_name="txids list",
                                    item_to_append=tx_information,
                                    item_name="tx_information"
                                )
                            else:
                                # NOTE: If this case executes, it means that sendTransaction never propagated the transaction
                                # to the network. This can unfortunatly happen sometimes, for some strange reason.
                                error_message = "The eth.sendTransaction generated the txid " + txid + \
                                                " even though the transaction was never popagted to the network. " \
                                                "Transaction object to send"
                                log_error(log, error_message, trans_object)
                    except requests.Timeout:
                        if tx_information is not None:
                            self.__append_to_list_and_log(
                                list_to_append_to=txids,
                                list_name="txids list",
                                item_to_append=tx_information,
                                item_name="tx_information"
                            )
                    except ValueError as v_ex:
                        if tx_information is not None:
                            self.__append_to_list_and_log(
                                list_to_append_to=txids,
                                list_name="txids list",
                                item_to_append=tx_information,
                                item_name="tx_information"
                            )
                        error_message = "Value error. Gas is most likely incorrectly calculated. Error message: " \
                                        + str(v_ex) + ". Occured for trans_object"
                        log_error(log, error_message, v_ex)
        except JSONRPCException as j_ex:
            error_message = "RPC error. Message from rpc client: " + str(j_ex)
            log_error(log, error_message, j_ex)
        except BaseException as ex:
            error_message = "Base exception error. Error message: " + str(ex)
            log_error(log, error_message, ex)

        # We want to make sure that we return any txids that actually succeeded, even if an exception was raised,
        # therefore we never return anything and just log the exception from the exception clauses,
        # and always return the txids.
        log_info(log, "Returning the following tx list from the send_to_addresses call", txids)
        return txids

    def handle_no_txid_returned_for_sendtransaction(self, trans_object, pending_balance_before_sent, pending_balance_after_sent,
                                                    pending_transactions_before_sent, pending_transactions_after_sent):
        error_message = "No txid was returned from eth.sendTransaction. Error message: "
        account = self.access.toChecksumAddress(trans_object['from'])

        for pending_transaction_after in pending_transactions_after_sent:
            pending_transaction_existed_before_sending = pending_transaction_after in pending_transactions_before_sent
            if not pending_transaction_existed_before_sending:
                #The pending transaction was added after the transaction was sent, therefore it must have been sent now.
                error_message += "A new transaction was found in the pending transactions that was not returned when " \
                                "sending the trans_object, which was"
                log_error(log, error_message, pending_transaction_after)
                txid = pending_transaction_after['hash']
                full_transaction_amount_trans_object = self.get_full_transaction_amount_in_wei(trans_object)
                new_transaction_found = self.do_get_transaction(txid)
                new_transaction_from_account = self.access.toChecksumAddress(new_transaction_found['from'])
                full_transaction_amount_new_transaction = self.get_full_transaction_amount_in_wei(new_transaction_found)
                if(full_transaction_amount_trans_object == full_transaction_amount_new_transaction
                    and account == new_transaction_from_account):
                    error_message = "A new transaction was found in the pending transactions that corresponds to the " \
                                     "trans_object. Returning the txid"
                    log_error(log, error_message, txid)
                    return txid

        if pending_balance_before_sent != pending_balance_after_sent:

                full_transaction_amount = self.get_full_transaction_amount_in_wei(trans_object)
                abs_difference = abs(pending_balance_before_sent - pending_balance_after_sent)
                if full_transaction_amount == abs_difference:
                    # A transaction has almost certainly happened! This is a serious error as we cant get the txid of
                    # the transaction that has happened.
                    likely_nonce = self.access.eth.getTransactionCount(account, "pending") - 1
                    error_message += "A transaction has most likely happened that has not been registred by the api. This" \
                                     " has happened for account: " + account + " With transaction nonce: " \
                                     + str(likely_nonce) + " Transaction object"
                    log_error(log, error_message, trans_object)
                    return None
                else:
                    error_message += "A transaction might have happened that has not been registered by the api. " \
                                     "Transaction object"
                    log_error(log, error_message, trans_object)
                    return None

        # it seems as if no transaction was actually transmitted.
        error_message += "txidBytes is None, this most likely means that a transaction was never broadcasted to the network."
        log_error(log, error_message, trans_object)
        return None


    def send_many(self, from_account="", minconf=1, from_wallet='', **amounts):
        send_amount_dict = amounts['amounts']
        txids = self.send_to_addresses(
            addresses_and_amounts = send_amount_dict,
            subtractfeefromamount=False,
            from_wallet=from_wallet)
        any_transaction_succeeded = len(txids) > 0
        return any_transaction_succeeded, txids

    def validate_that_geth_is_synced(self, total_elapsed_time=0.0, saved_highest_block=-1):

        #To be removed, only used for testing
        return

        #Base case
        if total_elapsed_time >= 30.0:
            exception_string = "The geth node is out of sync"
            raise JSONRPCException({'code': -343, 'message': exception_string})

        start_time = time.process_time()

        yml_config_reader = ConfigFileReader()
        api_key = yml_config_reader.get_api_key(api_key_service_name="etherscan")
        userdata = {"module": "proxy", "action": "eth_blockNumber", "apikey" : api_key}
        node_block_number = self.access.eth.blockNumber
        resp = requests.post('https://api.etherscan.io/api/', data=userdata)
        ether_scan_block_number = None
        try:
            ether_scan_block_number_hex = resp.json()['result']
            ether_scan_block_number = int(ether_scan_block_number_hex,0)
        except BaseException:
            log_error(log, "An error occoured when requesting the block number from etherscan, request response", resp)

        if ether_scan_block_number:
            block_number_difference = abs(ether_scan_block_number - node_block_number)
            node_blocks_are_not_ahead_of_etherscan = node_block_number <= ether_scan_block_number
            difference_is_unnacceptable = block_number_difference > yml_config_reader.get_offsync_acceptance(currency="eth")
            if node_blocks_are_not_ahead_of_etherscan and difference_is_unnacceptable:
                exception_string = "The geth node is out of sync"
                raise JSONRPCException({'code': -343, 'message': exception_string})

        # Either an error occoured when requesting the block number from etherscan, or our node is before etherscan
        syncing = self.access.eth.syncing
        if syncing is not False:
            current_block = int(str(syncing['currentBlock']))
            highest_block = int(str(syncing['highestBlock']))
            syncing_block_number_difference = abs(highest_block - current_block)

            # The reason we do this is because highest_block will be the highest block when the node starts syncing.
            # This means that if the node is syncing and this is our first time in the loop, we can't be sure if the
            # highest_block is acctually close to the real latest on the network block or not. Because of this
            # we only check if the range is in an acceptable range once the we know that highest block has actually
            # changed in the function calls.
            if saved_highest_block != -1 and highest_block != saved_highest_block:
                if syncing_block_number_difference > yml_config_reader.get_offsync_acceptance(currency="eth"):
                    exception_string = "The geth node is out of sync"
                    raise JSONRPCException({'code': -343, 'message': exception_string})
            else:
                time.sleep(3)
                elapsed_time_in_this_call = time.process_time() - start_time
                new_total_elapsed_time = elapsed_time_in_this_call + total_elapsed_time
                self.validate_that_geth_is_synced(
                    total_elapsed_time=new_total_elapsed_time,
                    saved_highest_block= highest_block
                )

    '''Throws requests.Timeout error if the endpoint timer has reached max time defined in config file'''
    def call_func_and_validate_timeout(self, func, func_args=None, log_message=None):
        if func_args:
            item_to_return = func(**func_args)
        else:
            item_to_return = func()
        if log_message:
            log_info(log, log_message,item_to_return)
        self.endpoint_timer.validate_is_within_timelimit()
        return item_to_return

    '''Throws requests.Timeout error if the endpoint timer has reached max time defined in config file'''
    def call_void_func_and_validate_timeout(self, func, func_args=None, log_message=None):
        if func_args:
            func(**func_args)
        else:
            func()
        if log_message:
            log_info(log, log_message)
        self.endpoint_timer.validate_is_within_timelimit()

    def __append_to_list_and_log(self, list_to_append_to, list_name, item_to_append, item_name):
        log_info(log, "Appending the following " + item_name + " to the " + list_name,
                 item_to_append)
        list_to_append_to.append(item_to_append)
        log_info(log, list_name + " after " + item_name + " was appended",
                 list_to_append_to)
