from decimal import Decimal

from bitcoinrpc.authproxy import JSONRPCException
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from btcrpc.utils import constantutil
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.log import get_log, log_info, log_error
from btcrpc.vo import transfers_using_sendtoaddress
from btcrpc.utils.semaphore import SemaphoreSingleton
from btcrpc.utils.rpc_calls.rpc_instance_generator import RpcGenerator
from btcrpc.utils.chain_enum import ChainEnum
from btcrpc.utils.endpoint_timer import EndpointTimer
import requests

import errno
from socket import error as socket_error

log = get_log("TransferUsingSendToAddress View")


class TransferCurrencyByUsingSendToAddress(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):
        endpoint_timer = EndpointTimer()
        log_info(log, "Request data", request.data)
        chain = ChainEnum.UNKNOWN
        semaphore = SemaphoreSingleton()
        global response_serializer
        post_serializer = transfers_using_sendtoaddress.PostParametersSerializer(data=request.data)

        yml_config = ConfigFileReader()

        if post_serializer.is_valid():
            log_info(log, "Post input data", post_serializer.data)
            transfer_list = post_serializer.data["transfers"]
            response_list = []
            try:
                if semaphore.acquire_if_released(log):
                    log_info(log, "Transfer list", transfer_list)
                    for transfer in transfer_list:
                        log_info(log, "Specific transfer to handle", transfer)
                        currency = transfer["currency"]
                        txFee = transfer["txFee"]
                        send_amount = transfer["amount"]
                        wallet = transfer["wallet"]
                        safe_address = transfer["safe_address"]
                        endpoint_timer.validate_is_within_timelimit()

                        rpc_call = RpcGenerator.get_rpc_instance(
                            wallet=wallet,
                            currency=currency,
                            endpoint_timer=endpoint_timer
                        )
                        log_info(log, "RPC instance class", rpc_call.__class__.__name__)
                        endpoint_timer.validate_is_within_timelimit()

                        chain = constantutil.check_service_chain(rpc_call)
                        log_info(log, "Chain", chain.value)
                        endpoint_timer.validate_is_within_timelimit()

                        encoding_flag = constantutil.get_safe_address_encoding(currency)
                        correct_encoded_safe_address = rpc_call.encode_address(
                            address=safe_address,
                            encoding_flag=encoding_flag)
                        log_info(log, "Safe address to try to send to", correct_encoded_safe_address)
                        endpoint_timer.validate_is_within_timelimit()

                        to_address = yml_config.get_safe_address_to_be_transferred(
                            currency=currency,
                            safe_address=correct_encoded_safe_address)
                        log_info(log, "To address after config file check", to_address)

                        to_address_is_invalid = not (rpc_call.do_validate_address(address=to_address))["isvalid"]
                        log_info(log, "To address is invalid is", to_address_is_invalid)
                        endpoint_timer.validate_is_within_timelimit()

                        wallet_balance = rpc_call.get_wallet_balance()
                        log_info(log, "The wallet balance is", wallet_balance)
                        endpoint_timer.validate_is_within_timelimit()

                        log_info(log, "Send amount is", send_amount)

                        if to_address_is_invalid:
                            error_message = "to_address is not valid"
                            response = self.create_transfer_information_response_and_log(
                                log_function=log_info,
                                log_message=error_message,
                                log_item=None,
                                currency=currency,
                                to_address=to_address,
                                amount=Decimal(str(send_amount)),
                                message=error_message,
                                status="fail")
                            self.append_to_response_list_and_log(response_list, response.__dict__)

                        elif wallet_balance < send_amount:
                            error_message = "Insufficient funds in wallet to send the requested amount. " \
                                            "Wallet balance is: " + str(wallet_balance) + \
                                            ". Amount to send is: " + str(send_amount)
                            response = self.create_transfer_information_response_and_log(
                                log_function=log_info,
                                log_message=error_message,
                                log_item=None,
                                currency=currency,
                                to_address=to_address,
                                amount=Decimal(str(send_amount)),
                                message=error_message,
                                status="fail")
                            self.append_to_response_list_and_log(response_list, response.__dict__)

                        else:
                            try:
                                log_info(log, "Trying to set the txfee to", str(txFee))
                                txfee_set = rpc_call.set_tx_fee(txFee)
                                log_info(log, "Using the suggested txfee " + str(txFee), txfee_set)
                                endpoint_timer.validate_is_within_timelimit()
                                # We don't validate the timeout after here, as we want to ensure that any sent txid is included
                                # in the list.

                                send_response_txids = rpc_call.send_to_address(
                                    address=to_address,
                                    amount=send_amount,
                                    subtractfeefromamount=True,
                                    from_wallet=wallet)
                                log_info(log, "Send response tx_id is", send_response_txids)

                                transactions_fee_infos = rpc_call.do_get_fees_of_transactions(send_response_txids)
                                log_info(log, "Transaction of txids is", transactions_fee_infos)

                                response = self.create_transfer_information_response_and_log(
                                    log_function=log_info,
                                    log_message="Creating successful transfer information response",
                                    log_item=None,
                                    currency=currency,
                                    to_address=to_address,
                                    amount=Decimal(str(send_amount)),
                                    message="Transfer is done",
                                    status="ok",
                                    transaction_fee_info_list=transactions_fee_infos)
                                self.append_to_response_list_and_log(response_list, response.__dict__)
                            except JSONRPCException as ex:
                                error_message = "Error: " + ex.error['message']
                                response = self.create_transfer_information_response_and_log(
                                    log_function=log_error,
                                    log_message=error_message,
                                    log_item=ex,
                                    currency=currency,
                                    to_address=to_address,
                                    amount=Decimal(str(send_amount)),
                                    message=error_message,
                                    status="fail")
                                self.append_to_response_list_and_log(response_list, response.__dict__)
                            # except (ConnectionError, ServerDown) as ex:
                            #     error_message = "Error: ConnectionError or ServerDown exception"
                            #     response = self.create_transfer_information_response_and_log(
                            #         log_function=log_error,
                            #         log_message=error_message,
                            #         log_item=ex,
                            #         currency=currency,
                            #         to_address=to_address,
                            #         amount=Decimal(str(send_amount)),
                            #         message=error_message,
                            #         status="fail")
                            #     self.append_to_response_list_and_log(response_list, response.__dict__)
                            except requests.Timeout as ex:
                                error_message = "The send request timed out. Exception message: " + str(ex)
                                response = self.create_transfer_information_response_and_log(
                                    log_function=log_error,
                                    log_message=error_message,
                                    log_item=ex,
                                    currency=currency,
                                    to_address=to_address,
                                    amount=Decimal(str(send_amount)),
                                    message=error_message,
                                    status="fail")
                                self.append_to_response_list_and_log(response_list, response.__dict__)
                                #We want to abort the transfer request if we timeout, so we reraise the exception.
                                raise ex

                    log_info(log, "Response list after transfers have been iterated", response_list)
                    semaphore.release(log)
                    transaction_has_failed = constantutil.check_for_failed_transactions(response_list)
                    if (transaction_has_failed):
                        error_message = "One or more transactions failed."
                        transfers_response = self.create_transfers_information_response_and_log(
                            log_error,
                            error_message + " Transfer response list",
                            response_list,
                            response_list=response_list,
                            chain=chain,
                            error=1,
                            error_message=error_message)
                    else:
                        transfers_response = self.create_transfers_information_response_and_log(
                            log_info,
                            "Creating successful Transfers response",
                            None,
                            response_list=response_list,
                            chain=chain)
                else:
                    error_message = "Semaphore is already acquired, wait until semaphore is released."
                    transfers_response = self.create_transfers_information_response_and_log(
                        log_error,
                        error_message,
                        None,
                        response_list=response_list,
                        chain=chain,
                        error=1,
                        error_message=error_message)
            except ValueError as ex:
                semaphore.release(log)
                error_message = "Error: %s" % str(ex)
                transfers_response = self.create_transfers_information_response_and_log(
                    log_error,
                    error_message,
                    ex,
                    response_list=response_list,
                    chain=chain,
                    error=1,
                    error_message=error_message)
            except JSONRPCException as ex:
                semaphore.release(log)
                error_message = "Bitcoin RPC error, check if username and password for node is correct. Message from " \
                                "python-bitcoinrpc: " + ex.message
                transfers_response = self.create_transfers_information_response_and_log(
                    log_error,
                    error_message,
                    ex,
                    response_list=response_list,
                    chain=chain,
                    error=1,
                    error_message=error_message)
            except requests.Timeout as ex:
                semaphore.release(log)
                error_message = "The request timed out. Transactions transferred before the timeout " \
                                "are included in the response_list list. " \
                                "Message from exception: " + str(ex)
                transfers_response = self.create_transfers_information_response_and_log(
                    log_error,
                    error_message,
                    ex,
                    response_list=response_list,
                    chain=chain,
                    error=1,
                    error_message=error_message)
            except socket_error as serr:
                semaphore.release(log)
                error_message = "Socket error: "
                if serr.errno != errno.ECONNREFUSED:
                    error_message = error_message + "A general socket error was raised."
                else:
                    error_message = error_message + "Connection refused error, check if the wallet node is down."

                transfers_response = self.create_transfers_information_response_and_log(
                    log_error,
                    error_message,
                    serr,
                    response_list=response_list,
                    chain=chain,
                    error=1,
                    error_message=error_message)
            except BaseException as ex:
                semaphore.release(log)
                error_message = "An exception was raised. Error message: " + str(ex)
                transfers_response = self.create_transfers_information_response_and_log(
                    log_error,
                    error_message,
                    ex,
                    response_list=response_list,
                    chain=chain,
                    error=1,
                    error_message=error_message)

            response_dict = transfers_response.__dict__
            log_info(log, "Full Transfer response", response_dict)

            response_serializer = transfers_using_sendtoaddress.TransfersInformationResponseSerializer(
                data=response_dict)
            log_info(log, "Response serializer", response_serializer)

            if response_serializer.is_valid():
                log_info(log, "The transfer response serializer was valid")
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                log_error(log, "The transfer response serializer was not valid",
                          response_serializer.errors)
                return Response(response_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

        log_error(log, "The post serializer was incorrect. Post serializer errors", post_serializer.errors)
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_transfer_information_response_and_log(self, log_function, log_message, log_item, currency, to_address="",
                                                     amount=Decimal(0), message="", status="", transaction_fee_info_list = []):
        log_function(log, log_message, log_item)
        transaction_fee_info_responses = \
            [transfers_using_sendtoaddress.TransactionWithFeeInformationResponse(trans.txid, trans.fee).__dict__
             for trans in transaction_fee_info_list]

        # Lines above can be replaced by the code below. This code does however mess upp the logging as it will include map objects.
        # transaction_fee_info_responses = map(
        #     lambda trans : transfers_using_sendtoaddress.TransactionWithFeeInformationResponse(trans.txid, trans.fee).__dict__,
        #     transaction_fee_info_list
        # )

        log_function(log, "The generated TransactionWithFeeInformationResponse list is", transaction_fee_info_responses)

        response = transfers_using_sendtoaddress.TransferInformationResponse(
            currency=currency,
            to_address=to_address,
            amount=amount,
            message=message,
            status=status,
            transaction_fee_infos=transaction_fee_info_responses
        )
        log_function(log, "The generated Transfer information response is", response.__dict__)
        return response

    def create_transfers_information_response_and_log(self, log_function, log_message, log_item, response_list, chain,
                                                      error=0, error_message=""):
        log_function(log, log_message, log_item)
        transfers_response = transfers_using_sendtoaddress.TransfersInformationResponse(
            transfers=response_list,
            chain=chain.value,
            error=error,
            error_message=error_message)
        log_function(log, "The generated Transfers information response is", transfers_response.__dict__)
        return transfers_response

    def append_to_response_list_and_log(self, response_list, response):
        log_info(log, "Appending the following response to the response_list",
                 response)
        response_list.append(response)
        log_info(log, "response_list after response was appended",
                 response_list)
