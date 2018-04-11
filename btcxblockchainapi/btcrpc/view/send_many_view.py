from bitcoinrpc.authproxy import JSONRPCException
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
# from sherlock import MCLock, LockTimeoutException, LockException
from pylibmc import ConnectionError, ServerDown
from rest_framework import status

from btcrpc.utils import constantutil
from btcrpc.utils.log import get_log, log_info, log_error
from btcrpc.vo import send_many_vo
import socket, errno
from socket import error as socket_error
from btcrpc.utils.semaphore import SemaphoreSingleton
from btcrpc.utils.rpc_calls.rpc_instance_generator import RpcGenerator
from btcrpc.utils.chain_enum import ChainEnum

log = get_log("SendMany view:")


class BTCSendManyView(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):
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
                rpc_call = RpcGenerator.get_rpc_instance(wallet=wallet, currency=currency)
                log_info(log, "RPC instance class", rpc_call.__class__.__name__)
                chain = constantutil.check_service_chain(rpc_call)
                log_info(log, "Chain", chain.value)

                if (semaphore.acquire_if_released(log)):
                    log_info(log, "Trying to set the txfee to", str(txFee))
                    txfee_set = rpc_call.set_tx_fee(txFee)
                    log_info(log, "Using the suggested txfee " + str(txFee), txfee_set)
                    isSuccess, transactions = rpc_call.send_many(from_account=from_account, from_wallet=wallet, amounts=amounts_dict)
                    log_info(log, "Is send many request successful", isSuccess)
                    log_info(log, "Transactions of send many request", transactions)

                    if (isSuccess):
                        semaphore.release(log)
                        for transaction in transactions:
                            try:
                                tx_ids_with_fee = rpc_call.do_get_fees_of_transactions(transaction.txids)
                                for tx_id_with_fee in tx_ids_with_fee:
                                    log_info(log, "Tx id with fee object", tx_id_with_fee)
                                    transaction_with_details = rpc_call.do_get_transaction_details(tx_id_with_fee)
                                    log_info(log, "Transaction with detail object", tx_id_with_fee)
                                    transactions_with_details_list.append(transaction_with_details)
                            except BaseException as e:
                                # Since we wan't to make sure that a successfull response actually is sent if the rpc sendmany succeeds
                                # we just continue no matter what exception we encounter
                                log_error(log, "An error occured when checking the transactions details", e)
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
                        semaphore.release(log)
                        error_message = "Not all of the transactions were successful, the transactions that succeeded are" \
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


                        # transaction = rpc_call.do_get_transaction(transactions)
                        # if transaction is None:
                        #     log_error(log,
                        #               "The transaction request with the txid:" + result + " did not result in a transaction.")
                        #     response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        #                                              fee=0,
                        #                                              message="BTC server - " + wallet + "is done.",
                        #                                              chain=chain.value, error=1)
                        #
                        # else:
                        #     log_info(log, "Transaction sent", transaction)
                        #     details = transaction["details"]
                        #     details_list = []
                        #     try:
                        #         for transactionDetail in details:
                        #             if (transactionDetail['category'] == 'send'):
                        #                 details_list.append(self.get_output_details(transactionDetail, result))
                        #         log_info(log, "Details list", details_list)
                        #     except BaseException as e:
                        #         # Since we wan't to make sure that a successfull response actually is sent if the rpc sendmany succeeds
                        #         # we just continue no matter what exception we encounter
                        #         log_error(log, "An error occured when checking the transactions details", e)
                        #
                        #     response = send_many_vo.SendManyResponse(
                        #         tx_id=result,
                        #         status=status.HTTP_200_OK,
                        #         fee=abs(transaction["fee"]),
                        #         message="Send many is done.",
                        #         chain=chain.value,
                        #         error=0,
                        #         error_message="",
                        #         details=details_list)

                    # elif transactions is not None and isinstance(transactions, JSONRPCException):
                    #     semaphore.release(log)
                    #     log_error(log, "Error: %s" % transactions.error['message'])
                    #     response = send_many_vo.SendManyResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    #                                              fee=0, message=transactions.error['message'],
                    #                                              chain=chain.value, error=1)
                    # elif transactions is not None and isinstance(transactions, socket.error):
                    #     semaphore.release(log)
                    #     log_error(log, "Error: Is the error an Econnrefused error:", transactions.errno == errno.ECONNREFUSED)
                    #     log_error(log, "Error message", transactions.message)
                    #     response = send_many_vo.SendManyResponse(
                    #         status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    #         fee=0,
                    #         message=transactions.message,
                    #         chain=chain.value,
                    #         error=1)

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

            except (ConnectionError, ServerDown) as ex:
                semaphore.release(log)
                error_message = "Error: ConnectionError or ServerDown exception"
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
            status=status.HTTP_200_OK,
            message=message,
            chain=chain.value,
            error=error,
            error_message=error_message,
            transactions=transactions_with_details_list)
        log_function(log, "The generated wallet balance response is", wallet_balance_response.__dict__)
        return wallet_balance_response
