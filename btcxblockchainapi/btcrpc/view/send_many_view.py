from bitcoinrpc.authproxy import JSONRPCException
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
# from sherlock import MCLock, LockTimeoutException, LockException
from rest_framework import status

from btcrpc.utils import constantutil
from btcrpc.utils.log import get_log, log_info, log_error
from btcrpc.vo import send_many_vo
import socket, errno
from socket import error as socket_error
from btcrpc.utils.semaphore import SemaphoreSingleton
from btcrpc.utils.rpc_calls.rpc_instance_generator import RpcGenerator
from btcrpc.utils.chain_enum import ChainEnum
from btcrpc.utils.endpoint_timer import EndpointTimer
import requests

log = get_log("SendMany view:")


class BTCSendManyView(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):
        endpoint_timer = EndpointTimer()
        log_info(log, "Request data", request.data)
        chain = ChainEnum.UNKNOWN
        semaphore = SemaphoreSingleton()
        serializer_post = send_many_vo.SendManyPostParametersSerializer(data=request.data)
        transactions_with_details_list = []

        if serializer_post.is_valid():
            log_info(log, "Post input data", serializer_post.data)
            currency = serializer_post.data["currency"]
            wallet = serializer_post.data["wallet"]
            txFee = serializer_post.data["txFee"]
            from_account = serializer_post.data['fromAddress']
            amounts = serializer_post.data['toSend']
            amounts_dict = dict()

            for amount in amounts:
                if amount['toAddress'] in amounts_dict:
                    # As the values in amounts_dict[amount['toAddress']] and amount['amount'] is a string, They need to be converted
                    current_amount = float(amounts_dict[amount['toAddress']])
                    extra_amount = float(amount['amount'])
                    new_amount = current_amount + extra_amount
                    amounts_dict[amount['toAddress']] = '%.9f' % new_amount
                else:
                    amounts_dict[amount['toAddress']] = amount['amount']
            log_info(log, "Amounts to send", amounts_dict)

            response = None

            try:
                rpc_call = RpcGenerator.get_rpc_instance(wallet=wallet, currency=currency, endpoint_timer=endpoint_timer)
                log_info(log, "RPC instance class", rpc_call.__class__.__name__)
                endpoint_timer.validate_is_within_timelimit()

                chain = constantutil.check_service_chain(rpc_call)
                log_info(log, "Chain", chain.value)
                endpoint_timer.validate_is_within_timelimit()

                if (semaphore.acquire_if_released(log)):
                    log_info(log, "Trying to set the txfee to", str(txFee))
                    txfee_set = rpc_call.set_tx_fee(txFee)
                    log_info(log, "Using the suggested txfee " + str(txFee), txfee_set)
                    endpoint_timer.validate_is_within_timelimit()

                    isSuccess, txids = rpc_call.send_many(from_account=from_account, from_wallet=wallet, amounts=amounts_dict)
                    # We want to make sure that transactions_with_details_list contains all txids that succeeded, no
                    # matter if the rest of the function below fails and raises exceptions, so that we atleast return
                    # any txids that succeeded
                    transactions_with_details_list = constantutil.create_transaction_object_dict_list_from_transaction_object_list(
                        constantutil.create_transaction_object_list_from_txids(txids))

                    log_info(log, "Is send many request successful", isSuccess)
                    log_info(log, "Transactions of send many request", txids)
                    # NOTE! We add this check after we have included the txids in the transactions_with_details_list, as
                    # we need to ensure that they are returned no matter what.
                    endpoint_timer.validate_is_within_timelimit()

                    if (isSuccess):
                        semaphore.release(log)
                        txids_with_fee = rpc_call.do_get_fees_of_transactions(txids)
                        endpoint_timer.validate_is_within_timelimit()

                        txids_with_fee_transaction_object_list = \
                            constantutil.create_transaction_object_list_from_transaction_fee_info_list(txids_with_fee)

                        self.validate_that_length_is_equal_or_longer(
                            txids_with_fee_transaction_object_list,
                            transactions_with_details_list,
                            "rpc_call.do_get_fees_of_transactions"
                        )
                        #Update the transactions_with_details_list with the new info since validate call succeeded
                        transactions_with_details_list = \
                            constantutil.create_transaction_object_dict_list_from_transaction_object_list(
                                txids_with_fee_transaction_object_list)

                        updated_transaction_with_details = []
                        for transaction_object in txids_with_fee_transaction_object_list:
                            log_info(log, "Txid with fee object", transaction_object)
                            transaction_with_details = rpc_call.do_get_transaction_details(transaction_object)
                            endpoint_timer.validate_is_within_timelimit()
                            log_info(log, "Transaction with details object", transaction_with_details)
                            updated_transaction_with_details.append(transaction_with_details)

                        self.validate_that_length_is_equal_or_longer(
                            updated_transaction_with_details,
                            transactions_with_details_list,
                            "rpc_call.do_get_transaction_details"
                        )
                        # Update the transactions_with_details_list with the new info since validate call succeeded
                        transactions_with_details_list = \
                            constantutil.create_transaction_object_dict_list_from_transaction_object_list(
                                updated_transaction_with_details)

                        # note that we are send in the updated_transaction_with_details that includes TransactionObjects
                        # and not the dict objects. This is so we can call the class properties and do not need to access
                        # the dictionary in the amounts_dict_total_amount_matches_details_list function.
                        if self.amounts_dict_total_amount_matches_details_list\
                                (amounts_dict, updated_transaction_with_details):
                            response = self.create_send_many_response_and_log(
                                log_function=log_info,
                                log_message="Send many is done.",
                                log_item=None,
                                status=status.HTTP_200_OK,
                                message="Send many is done.",
                                transactions_with_details_list=transactions_with_details_list,
                                chain=chain,
                                error=0,
                                error_message="")
                        else:
                            error_message = "It seems as not all of the total amount requested to send was actually sent. " \
                                            "This indicates that not all trnasactions were executed successfully."
                            response = self.create_send_many_response_and_log(
                                log_function=log_error,
                                log_message=error_message,
                                log_item=None,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                message=error_message,
                                transactions_with_details_list=transactions_with_details_list,
                                chain=chain,
                                error=1,
                                error_message=error_message)

                    else:
                        semaphore.release(log)
                        error_message = "Not all of the transactions were successful, the transactions that succeeded are " \
                                        "included in the transactions list"
                        response = self.create_send_many_response_and_log(
                            log_function=log_error,
                            log_message=error_message,
                            log_item=None,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            message=error_message,
                            transactions_with_details_list=transactions_with_details_list,
                            chain=chain,
                            error=1,
                            error_message=error_message)

                else:
                    error_message = "Error: The semaphore is already required, wait until semaphore is released"
                    response = self.create_send_many_response_and_log(
                        log_function=log_error,
                        log_message=error_message,
                        log_item=None,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        message=error_message,
                        transactions_with_details_list=transactions_with_details_list,
                        chain=chain,
                        error=1,
                        error_message=error_message)

            # except (ConnectionError, ServerDown) as ex:
            #     semaphore.release(log)
            #     error_message = "Error: ConnectionError or ServerDown exception"
            #     response = self.create_send_many_response_and_log(
            #         log_function=log_error,
            #         log_message=error_message,
            #         log_item=ex,
            #         status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            #         message=error_message,
            #         transactions_with_details_list=transactions_with_details_list,
            #         chain=chain,
            #         error=1,
            #         error_message=error_message)

            except JSONRPCException as ex:
                semaphore.release(log)
                error_message = "Bitcoin RPC error, check if username and password for node is correct. Message from " \
                                "python-bitcoinrpc: " + ex.message
                response = self.create_send_many_response_and_log(
                    log_function=log_error,
                    log_message=error_message,
                    log_item=ex,
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=error_message,
                    transactions_with_details_list=transactions_with_details_list,
                    chain=chain,
                    error=1,
                    error_message=error_message)

            except requests.Timeout as ex:
                semaphore.release(log)
                error_message = "The request timed out. Transactions genereated before the timeout " \
                                "is included in the transactions_with_details_list list. " \
                                "Message from exception: " + str(ex)
                response = self.create_send_many_response_and_log(
                    log_function=log_error,
                    log_message=error_message,
                    log_item=ex,
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=error_message,
                    transactions_with_details_list=transactions_with_details_list,
                    chain=chain,
                    error=1,
                    error_message=error_message)

            except socket_error as serr:
                semaphore.release(log)
                error_message = "Error: "
                if serr.errno != errno.ECONNREFUSED:
                    error_message = error_message + "A general socket error was raised."
                else:
                    error_message = error_message + "Connection refused error, check if the wallet node is down."
                response = self.create_send_many_response_and_log(
                    log_function=log_error,
                    log_message=error_message,
                    log_item=serr,
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=error_message,
                    transactions_with_details_list=transactions_with_details_list,
                    chain=chain,
                    error=1,
                    error_message=error_message)

            except BaseException as ex:
                semaphore.release(log)
                error_message = "An exception was raised. Error message: " + str(ex)
                response = self.create_send_many_response_and_log(
                    log_function=log_error,
                    log_message=error_message,
                    log_item=ex,
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=error_message,
                    transactions_with_details_list=transactions_with_details_list,
                    chain=chain,
                    error=1,
                    error_message=error_message)

            if response is not None:
                send_many_response_serializer = send_many_vo.SendManyResponseSerializer(data=response.__dict__)
            else:
                error_message = "Error: response is None"
                response = self.create_send_many_response_and_log(
                    log_function=log_error,
                    log_message=error_message,
                    log_item=None,
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=error_message,
                    transactions_with_details_list=transactions_with_details_list,
                    chain=chain,
                    error=1,
                    error_message=error_message)
                send_many_response_serializer = send_many_vo.SendManyResponseSerializer(data=response.__dict__)

            log_info(log, "Send many response serializer", send_many_response_serializer)
            if send_many_response_serializer.is_valid():
                log_info(log, "The response send_many_response_serializer was valid. The serializer data is",
                         send_many_response_serializer.data)
                return Response(send_many_response_serializer.data, status=status.HTTP_200_OK)
            else:
                semaphore.release(log)
                log_error(log, "The response send_many_response_serializer was not valid.",
                          send_many_response_serializer.errors)
                return Response(send_many_response_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

        log_error(log, "The post serializer was incorrect. Post serializer errors", serializer_post.errors)
        return Response(serializer_post.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_send_many_response_and_log(self, log_function, log_message, log_item, status, message,
                                          transactions_with_details_list, chain, error=0, error_message=""):
        log_function(log, log_message, log_item)
        wallet_balance_response = send_many_vo.SendManyResponse(
            status=status,
            message=message,
            chain=chain.value,
            error=error,
            error_message=error_message,
            transactions=transactions_with_details_list)
        log_function(log, "The generated send many response is", wallet_balance_response.__dict__)
        return wallet_balance_response

    def validate_that_length_is_equal_or_longer(self, new_transactions_with_details_list, transactions_with_details_list,
                                                last_function_call_name):
        if not len(new_transactions_with_details_list) >= len(transactions_with_details_list):
            exception_string = "One or more txids was lost during the " + last_function_call_name + " call."
            raise JSONRPCException({'code': -343, 'message': exception_string})

    def amounts_dict_total_amount_matches_details_list(self, amounts_dict, transactions_with_details_list):
        amounts_dict_total_amount = 0
        for to_address, amount in amounts_dict.items():
            amounts_dict_total_amount += float(amount)

        transactions_with_details_list_total_amount = 0
        for transaction in transactions_with_details_list:
            for detail in transaction.details:
                transactions_with_details_list_total_amount += float(detail.amount)

        return amounts_dict_total_amount == transactions_with_details_list_total_amount

