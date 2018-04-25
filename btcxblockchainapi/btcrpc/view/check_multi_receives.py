from datetime import datetime
from decimal import *

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from bitcoinrpc.authproxy import JSONRPCException
from btcrpc.utils import constantutil
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.log import get_log, log_info, log_error
from btcrpc.vo import check_multi_receives
import errno
from socket import error as socket_error
from btcrpc.utils.rpc_calls.rpc_call import RPCCall
from btcrpc.utils.rpc_calls.rpc_instance_generator import RpcGenerator
from btcrpc.utils.chain_enum import ChainEnum

log = get_log("CheckMultiAddressesReceive view")
yml_config = ConfigFileReader()
RISK_LOW_CONFIRMATIONS = yml_config.get_confirmations_mapping_to_risk(currency='btc', risk='low')
RISK_MEDIUM_CONFIRMATIONS = yml_config.get_confirmations_mapping_to_risk(currency='btc', risk='medium')
RISK_HIGH_CONFIRMATIONS = yml_config.get_confirmations_mapping_to_risk(currency='btc', risk='high')


class CheckMultiAddressesReceive(APIView):
    def post(self, request):
        log_info(log, "Request data", request.data)
        chain = ChainEnum.UNKNOWN
        post_serializers = check_multi_receives.PostParametersSerializer(data=request.data)

        response_list = []
        if post_serializers.is_valid():
            log_info(log, "Post input data", post_serializers.data)
            transactions = post_serializers.data["transactions"]
            log_info(log, "Transactions to iterate over", transactions)
            try:
                any_receive_has_error = False
                for transaction in transactions:
                    log_info(log, "Transaction", transaction)

                    wallet = transaction["wallet"]
                    currency = transaction["currency"]

                    rpc_call = RpcGenerator.get_rpc_instance(wallet=wallet, currency=currency)
                    log_info(log, "RPC instance class", rpc_call.__class__.__name__)
                    chain = constantutil.check_service_chain(rpc_call)
                    log_info(log, "Chain", chain.value)

                    transaction_address = transaction["address"]

                    address_validation = rpc_call.do_validate_address(address=transaction_address)
                    log_info(log, "Address validation", address_validation)

                    if address_validation["isvalid"] is False:
                        any_receive_has_error = True
                        error_message = transaction_address + " is not a valid address"
                        log_error(log, error_message)
                        response = check_multi_receives.ReceiveInformationResponse(
                            currency=transaction["currency"],
                            address=transaction_address,
                            received=0.0,
                            risk="low",
                            txs=[],
                            error=1,
                            error_message=error_message)
                        response_list.append(response.__dict__)
                        continue

                    if address_validation["ismine"] is False:
                        any_receive_has_error = True
                        error_message = transaction_address + " is not an address of the wallet"
                        log_error(log, error_message)
                        response = check_multi_receives.ReceiveInformationResponse(
                            currency=transaction["currency"],
                            address=transaction_address,
                            received=0.0,
                            risk="low",
                            txs=[],
                            error=1,
                            error_message=error_message)
                        response_list.append(response.__dict__)
                        continue

                    tx_ids = self.__get_txIds(rpc_service=rpc_call, account=transaction["address"])

                    received_with_risk = self.__receive_amount_for_risk(
                        rpc_service=rpc_call,
                        wallet_address=transaction_address,
                        tx_ids=tx_ids)

                    received = Decimal(received_with_risk["result"]) if received_with_risk else 0.0
                    log_info(log, "Total amount received", received)
                    risk = received_with_risk["risk"] if received_with_risk else "low"
                    log_info(log, "Received " + str(received) + " with risk " + risk)

                    response = self.create_receive_information_response_and_log(
                        log_info,
                        "Generating successful receive information response",
                        None,
                        currency=transaction["currency"],
                        address=transaction_address,
                        received=received,
                        risk=risk,
                        txs=tx_ids)
                    response_list.append(response.__dict__)
                    log_info(log, "Response list after receive information response has been appended", response_list)
                if not any_receive_has_error:
                    receives_response = self.create_receives_information_response_and_log(
                        log_info,
                        "Generating successful receives information response",
                        None,
                        response_list=response_list,
                        chain=chain)
                else:
                    error_message = "One of more receivement checks failed"
                    receives_response = self.create_receives_information_response_and_log(
                        log_error,
                        error_message,
                        None,
                        response_list=response_list,
                        chain=chain,
                        error=1,
                        error_message=error_message
                    )
            except JSONRPCException as ex:

                error_message = "Bitcoin RPC error, check if username and password for node is correct. Message from " \
                                "python-bitcoinrpc: " + ex.message
                receives_response = self.create_receives_information_response_and_log(
                    log_error,
                    error_message,
                    ex,
                    response_list=response_list,
                    chain=chain,
                    error=1,
                    error_message=error_message
                )
            except socket_error as serr:
                error_message = "Socket error: "
                if serr.errno != errno.ECONNREFUSED:
                    error_message = error_message + "A general socket error was raised."
                else:
                    error_message = error_message + "Connection refused error, check if the wallet node is down."

                receives_response = self.create_receives_information_response_and_log(
                    log_error,
                    error_message,
                    serr,
                    response_list=response_list,
                    chain=chain,
                    error=1,
                    error_message=error_message
                )
            except BaseException as ex:
                error_message = "An exception was raised. Error message: " + str(ex)
                receives_response = self.create_receives_information_response_and_log(
                    log_error,
                    error_message,
                    ex,
                    response_list=response_list,
                    chain=chain,
                    error=1,
                    error_message=error_message
                )

            response_dict = receives_response.__dict__
            log_info(log, "Full receives response", response_dict)

            response_serializer = check_multi_receives.ReceivesInformationResponseSerializer(data=response_dict)
            log_info(log, "Response serializer", response_serializer)

            if response_serializer.is_valid():
                log_info(log, "The response_serializer was valid")
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                log_error(log, "The response_serializer was not valid", response_serializer.errors)
                return Response(response_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

        log_error(log, "The post serializer was incorrect. Post serializer errors", post_serializers.errors)
        return Response(post_serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def __receive_amount_for_risk(self, rpc_service, wallet_address="", tx_ids=[]):

        if not isinstance(rpc_service, RPCCall):
            raise TypeError("Expected object BTCRPCCall, got %s" % (type(rpc_service),))

        result = Decimal(
            rpc_service.amount_received_by_address(address=wallet_address, confirms=RISK_HIGH_CONFIRMATIONS))
        log_info(log, "Total amount received by address " + wallet_address, result)

        low_risk_counter = 0
        medium_risk_counter = 0
        high_risk_counter = 0

        log_info(log, "Transactions to iterate over to check confirmations", tx_ids)

        for tx_id in tx_ids:
            log_info(log, ''.join(["tx_id confirmation is ", str(tx_id["confirmations"]), " for transaction"]), tx_id)
            if tx_id["confirmations"] == RISK_HIGH_CONFIRMATIONS:
                high_risk_counter += 1
            if tx_id["confirmations"] >= RISK_MEDIUM_CONFIRMATIONS and tx_id["confirmations"] < RISK_LOW_CONFIRMATIONS:
                medium_risk_counter += 1
            if tx_id["confirmations"] >= RISK_LOW_CONFIRMATIONS:
                low_risk_counter += 1

        log_info(log, ''.join(["low_risk_counter: ", str(low_risk_counter), ", medium_risk_counter: "
                                  , str(medium_risk_counter), ", high_risk_counter: ", str(high_risk_counter)]))

        received_with_risk = {"result": result, "risk": 'low'}
        if medium_risk_counter >= 1:
            received_with_risk = {"result": result, "risk": 'medium'}
        if high_risk_counter >= 1:
            received_with_risk = {"result": result, "risk": 'high'}

        log_info(log, "Received with risk", received_with_risk)
        return received_with_risk

    def __get_txIds(self, rpc_service, account=""):

        if not isinstance(rpc_service, RPCCall):
            raise TypeError("Expected object BTCRPCCall, got %s" % (type(rpc_service),))

        transactions = rpc_service.list_transactions(account=account, count=100000)
        log_info(log, "transactions for account " + account, transactions)
        transactions_with_tx_id = []

        for transaction in transactions:
            if 'txid' in transaction and transaction['category'] == 'receive':
                transaction_with_tx_id = check_multi_receives.TxIdTransaction(
                    txid=transaction['txid'],
                    received=transaction['amount'],
                    confirmations=transaction['confirmations'],
                    date=datetime.fromtimestamp(transaction['time']))
                transactions_with_tx_id.append(transaction_with_tx_id.__dict__)
                log_info(log, "transactions received of category receive added to list",
                         transaction_with_tx_id.__dict__)

        # txIds = map(lambda transaction: transaction['txid'], transactions_with_tx_id)
        log_info(log, "transactions received of category receive for the specific account " + account,
                 transactions_with_tx_id)
        return transactions_with_tx_id

    def create_receive_information_response_and_log(self, log_function, log_message, log_item, currency, address,
                                                    received,
                                                    risk, txs):
        log_function(log, log_message, log_item)
        receive_info_response = check_multi_receives.ReceiveInformationResponse(
            currency=currency,
            address=address,
            received=received,
            risk=risk,
            txs=txs)
        log_function(log, "The generated Receive Information Response is", receive_info_response.__dict__)
        return receive_info_response

    def create_receives_information_response_and_log(self, log_function, log_message, log_item, response_list, chain,
                                                     error=0, error_message=""):
        log_function(log, log_message, log_item)
        receives_response = check_multi_receives.ReceivesInformationResponse(
            receives=response_list,
            chain=chain.value,
            error=error,
            error_message=error_message)
        log_function(log, "The generated Receives Information Response is", receives_response.__dict__)
        return receives_response
