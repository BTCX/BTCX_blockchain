from datetime import datetime
from decimal import *

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from btcrpc.utils import constantutil
from btcrpc.utils.btc_rpc_call import BTCRPCCall
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.log import get_log
from btcrpc.vo import check_multi_receives

log = get_log("CheckMultiAddressesReceive view")
yml_config = ConfigFileReader()
RISK_LOW_CONFIRMATIONS = yml_config.get_confirmations_mapping_to_risk(currency='btc', risk='low')
RISK_MEDIUM_CONFIRMATIONS = yml_config.get_confirmations_mapping_to_risk(currency='btc', risk='medium')
RISK_HIGH_CONFIRMATIONS = yml_config.get_confirmations_mapping_to_risk(currency='btc', risk='high')


class CheckMultiAddressesReceive(APIView):
  def post(self, request):
    log.info(request.DATA)
    post_serializers = check_multi_receives.PostParametersSerializer(data=request.DATA)
    btc_rpc_call = BTCRPCCall()
    is_test_net = constantutil.check_service_is_test_net(btc_rpc_call)

    response_list = []
    if post_serializers.is_valid():
      log.info(post_serializers.data["transactions"])
      transactions = post_serializers.data["transactions"]
      for transaction in transactions:
        log.info(transaction)

        transaction_address = transaction["address"]

        address_validation = btc_rpc_call.do_validate_address(address=transaction_address)

        if address_validation["isvalid"] is False:
          return Response(transaction_address + " is not a valid address",
                          status=status.HTTP_400_BAD_REQUEST)

        tx_ids = self.__get_txIds(transaction["address"], btc_service=btc_rpc_call)
        log.debug(tx_ids)

        received_with_risk = self.__receive_amount_for_risk(wallet_address=transaction_address,
                                                            tx_ids=tx_ids,
                                                            btc_service=btc_rpc_call)

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
                                                                           test=is_test_net)
      response_dict = receives_response.__dict__

      response_serializer = check_multi_receives.ReceivesInformationResponseSerializer(data=response_dict)

      if response_serializer.is_valid():
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
      else:
        return Response(response_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

    return Response(post_serializers.errors, status=status.HTTP_400_BAD_REQUEST)

  def __receive_amount_for_risk(self, wallet_address="", tx_ids=[], btc_service=BTCRPCCall()):

    if not isinstance(btc_service, BTCRPCCall):
      raise TypeError("Expected object BTCRPCCall, got %s" % (type(btc_service),))

    result = Decimal(
      btc_service.amount_received_by_address(address=wallet_address, confirms=RISK_HIGH_CONFIRMATIONS))

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

  def __get_txIds(self, account="", btc_service=BTCRPCCall()):

    if not isinstance(btc_service, BTCRPCCall):
      raise TypeError("Expected object BTCRPCCall, got %s" % (type(btc_service),))

    transactions = btc_service.list_transactions(account=account, count=88)
    transactions_with_tx_id = []

    for transaction in transactions:
      if 'txid' in transaction and transaction['category'] == 'receive':
        transaction_with_tx_id = check_multi_receives.TxIdTransaction(txid=transaction['txid'],
                                                                      received=transaction['amount'],
                                                                      confirmations=transaction['confirmations'],
                                                                      date=datetime.fromtimestamp(transaction['time']))
        transactions_with_tx_id.append(transaction_with_tx_id.__dict__)

    # txIds = map(lambda transaction: transaction['txid'], transactions_with_tx_id)
    return transactions_with_tx_id
