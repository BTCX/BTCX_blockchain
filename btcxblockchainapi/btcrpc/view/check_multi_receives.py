from datetime import datetime
from decimal import *

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from bitcoinrpc.authproxy import JSONRPCException
from btcrpc.utils import constantutil
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.log import get_log
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
        chain = ChainEnum.UNKNOWN
        log.info(request.data)
        post_serializers = check_multi_receives.PostParametersSerializer(data=request.data)

        response_list = []
        if post_serializers.is_valid():
            log.info(post_serializers.data["transactions"])
            transactions = post_serializers.data["transactions"]
            try:
                for transaction in transactions:
                    log.info(transaction)

                    wallet = transaction["wallet"]
                    currency = transaction["currency"]

                    rpc_call = RpcGenerator.get_rpc_instance(wallet=wallet, currency=currency)
                    chain = constantutil.check_service_chain(rpc_call)

                    transaction_address = transaction["address"]

                    address_validation = rpc_call.do_validate_address(address=transaction_address)

                    if address_validation["isvalid"] is False:
                        error_message = transaction_address + " is not a valid address"
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
                        error_message = transaction_address + " is not an address of the wallet"
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

                    tx_ids = self.__get_txIds(
                        rpc_service=rpc_call, address=transaction["address"])
                    log.debug(tx_ids)

                    received_with_risk = self.__receive_amount_for_risk(rpc_service=rpc_call,
                                                                        wallet_address=transaction_address,
                                                                        tx_ids=tx_ids)

                    received = Decimal(received_with_risk["result"]) if received_with_risk else 0.0
                    risk = received_with_risk["risk"] if received_with_risk else "low"
                    log.info("received: %f, risk: %s", received, risk)

                    response = check_multi_receives.ReceiveInformationResponse(currency=transaction["currency"],
                                                                               address=transaction_address,
                                                                               received=received,
                                                                               risk=risk,
                                                                               txs=tx_ids)
                    response_list.append(response.__dict__)
                receives_response = check_multi_receives.ReceivesInformationResponse(receives=response_list,
                                                                                         chain=chain.value)

            except JSONRPCException as ex:
                log.error("Error: %s" % ex.error['message'])
                error_message = "Bitcoin RPC error, check if username and password for node is correct. Message from " \
                                "python-bitcoinrpc: " + ex.message
                receives_response = check_multi_receives.ReceivesInformationResponse(receives=response_list,
                                                                                     chain=chain.value,
                                                                                     error=1,
                                                                                     error_message=error_message
                                                                                     )
            except socket_error as serr:
                if serr.errno != errno.ECONNREFUSED:
                    receives_response = check_multi_receives.ReceivesInformationResponse(receives=response_list,
                                                                                         chain=chain.value,
                                                                                         error=1,
                                                                                         error_message="A general socket error was raised."
                                                                                         )
                else:
                    receives_response = check_multi_receives.ReceivesInformationResponse(receives=response_list,
                                                                                         chain=chain.value,
                                                                                         error=1,
                                                                                         error_message="Connection refused error, "
                                                                                                       "check if the wallet node is down."
                                                                                         )
            except BaseException as ex:
                log.error("Error: %s" % str(ex))
                error_message = "An exception was raised. Error message: " + str(ex)
                receives_response = check_multi_receives.ReceivesInformationResponse(receives=response_list,
                                                                                     chain=chain.value,
                                                                                     error=1,
                                                                                     error_message=error_message
                                                                                     )

            response_dict = receives_response.__dict__

            response_serializer = check_multi_receives.ReceivesInformationResponseSerializer(data=response_dict)

            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(response_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

        return Response(post_serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def __receive_amount_for_risk(self, rpc_service, wallet_address="", tx_ids=[]):

        if not isinstance(rpc_service, RPCCall):
            raise TypeError("Expected object BTCRPCCall, got %s" % (type(rpc_service),))

        result = Decimal(
            rpc_service.amount_received_by_address(address=wallet_address, confirms=RISK_HIGH_CONFIRMATIONS))

        low_risk_counter = 0
        medium_risk_counter = 0
        high_risk_counter = 0

        for tx_id in tx_ids:
            log.info("tx_id confirmation is %d.", tx_id["confirmations"])
            if tx_id["confirmations"] == RISK_HIGH_CONFIRMATIONS:
                high_risk_counter += 1
            if tx_id["confirmations"] >= RISK_MEDIUM_CONFIRMATIONS and tx_id["confirmations"] < RISK_LOW_CONFIRMATIONS:
                medium_risk_counter += 1
            if tx_id["confirmations"] >= RISK_LOW_CONFIRMATIONS:
                low_risk_counter += 1

        log.info("low_risk_counter: %d, medium_risk_counter: %d, high_risk_counter: %d",
                 low_risk_counter, medium_risk_counter, high_risk_counter)

        if high_risk_counter >= 1:
            log.info("received with 0 confirmed")
            log.info(result)
            log.info("high")
            return {"result": result, "risk": 'high'}

        if medium_risk_counter >= 1:
            log.info("received with 1 confirmed")
            log.info(result)
            log.info("medium")
            return {"result": result, "risk": 'medium'}

        if low_risk_counter >= 1:
            log.info("received with 6 confirmed")
            log.info(result)
            log.info("low")
            return {"result": result, "risk": 'low'}

    """def __get_txIds(self, rpc_service, account=""):

        if not isinstance(rpc_service, RPCCall):
            raise TypeError("Expected object BTCRPCCall, got %s" % (type(rpc_service),))

        transactions = rpc_service.list_transactions(account=account, count=88)
        transactions_with_tx_id = []

        for transaction in transactions:
            if 'txid' in transaction and transaction['category'] == 'receive':
                transaction_with_tx_id = check_multi_receives.TxIdTransaction(txid=transaction['txid'],
                                                                              received=transaction['amount'],
                                                                              confirmations=transaction[
                                                                                  'confirmations'],
                                                                              date=datetime.fromtimestamp(
                                                                                  transaction['time']))
                transactions_with_tx_id.append(transaction_with_tx_id.__dict__)

        # txIds = map(lambda transaction: transaction['txid'], transactions_with_tx_id)
        return transactions_with_tx_id"""

    def __get_txIds(self, rpc_service, address=""):

        if not isinstance(rpc_service, RPCCall):
            raise TypeError(
                "Expected object BTCRPCCall, got %s" % (type(rpc_service),))

        received_res_list = rpc_service.list_received_by_address(
            address=address)
        transactions_with_tx_id = []

        if len(received_res_list) == 0:
            return transactions_with_tx_id

        received_res = received_res_list[0]
        for txid in received_res['txids']:
            tx_info = rpc_service.do_get_transaction(txid)
            received_amount = Decimal(0)
            for detail in tx_info['details']:
                is_received = detail['category'] == "receive"
                is_correct_address = detail['address'] == address
                if is_received and is_correct_address:
                    received_amount += detail['amount']
            transaction_with_tx_id = check_multi_receives.TxIdTransaction(
                txid=txid,
                received=received_amount,
                confirmations=tx_info['confirmations'],
                date=datetime.fromtimestamp(tx_info['time']))
            transactions_with_tx_id.append(transaction_with_tx_id.__dict__)

        return transactions_with_tx_id
