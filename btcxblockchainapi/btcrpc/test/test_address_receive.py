from django.test import TestCase
from btcrpc import btc_rpc_call
from btcrpc.utils.timeUtil import TimeUtils
from btcrpc.utils.jsonutil import JsonUtils
import simplejson
from btcrpc.log import *
from btcrpc.vo.api_output_result import AddressReceiveOutputAttributeConst
from ddt import ddt, data
from btcrpc.vo.check_multi_receive import *
from btcrpc.constants import riskconstants

log = get_log("test_address_receive")

@ddt
class BTCRPCTestCase(TestCase):

    def setUp(self):
        self.btc_RPC_call = btc_rpc_call.BTCRPCCall()

    @data(1347517119)
    def test_epoch_time_to_datetime(self, value):
        epoch_time = TimeUtils.epoch_to_datetime(value)
        print epoch_time
        self.assertEquals(epoch_time, '2012-09-13 06:18:39')
    """
    def test_address_receive_btc(self):
        transactions_log = self.btc_RPC_call.do_list_transactions("n4LSoNto3TobC6ToxstxRXT3V9TpZa1ydi")
        #print transactions_log["account"]
        #print jsonutil.JsonUtils.is_json(transactions_log)
        
        transactions_log_json = simplejson.dumps(transactions_log, use_decimal=True)
        log.info(transactions_log_json)

        log.info(JsonUtils.is_json(transactions_log_json))        

        #object = simplejson.loads(transactions_log)
        log.info(transactions_log[0])
        
        for o in transactions_log:
            log.info(o["amount"])
            log.info(o["address"])
            log.info( o["txid"])
            log.info(TimeUtils.epoch_to_datetime(o["timereceived"]))
            log.info(TimeUtils.epoch_to_datetime(o["blocktime"]))
            log.info(o["confirmations"])
    """

    """
    def test_address_receive_btc_with_txid(self):
        transactions_log  = self.btc_RPC_call.do_get_transaction("61b34a7c10ddd9f278207b44c5635440c85f5fa082fcf2d440f8b763a3659649")
        transactions_log_json = simplejson.dumps(transactions_log, use_decimal=True)

        log.info(transactions_log_json)

        attributeConst = AddressReceiveOutputAttributeConst()
        log.info(transactions_log[attributeConst.TXID])
        log.info(transactions_log[attributeConst.AMOUNT])
        log.info(transactions_log["details"][0][attributeConst.ADDRESS])
        log.info(TimeUtils.epoch_to_datetime(transactions_log[attributeConst.TIMERECEIVED]))
        log.info(TimeUtils.epoch_to_datetime(transactions_log[attributeConst.BLOCKTIME]))
    """

    def test_post_serializer_for_multi_receive(self):
        test_data = {"transactions": [{"currency": "btc", "address": "mkRRcxbKLpy8zm1K8ARmRZ5gAuPq1ipufM", "amount": 0.1},
                                    {"currency": "btc", "address": "mwtg7rSERQRCbsHLnon7dhN86kur5o77V5", "amount": 0.2}],"test": True}
        log.info(test_data)
        post_serializer = PostParametersSerializer(data=test_data)
        self.assertTrue(post_serializer.is_valid())
        log.info(post_serializer.errors)

    def test_response_serializer_for_multi_receive(self):
        test_data = [{"currency": "btc", "address": "mkRRcxbKLpy8zm1K8ARmRZ5gAuPq1ipufM", "received": 0.0, "risk": "high",
                      "txids": ["51b78168d94ec307e2855697209275d477e05d8647caf29cb9e38fb6a4661145", "22e889379baded3814fa28d2d4a678fd810d76edc96c91589496aadf4600eaa6"]},
                     {"currency": "btc", "address": "mwtg7rSERQRCbsHLnon7dhN86kur5o77V5", "received": 0.0, "risk": "low",
                      "txids": ["2deaf5db1545124a0868ab55cd6fd8b0dcaffb527731078e5088fe1c703b05a8"]},]

        response_serializer = ReceiveInformationResponseSerializer(data=test_data, many=True)
        log.info(response_serializer.is_valid())
        self.assertTrue(response_serializer.is_valid())
        log.info(response_serializer.errors)

    def test_receive_amount_for_risk(self):
        #address="n3AKNG5vNXtQS4Ci7YQVQHRs5fuX3M3wor"
        address="mopxUEXSLv8Auc8AgAdHAjBwwUQeWjsGN2"
        expected_amount = 0.2

        result = float(btc_rpc_call.BTCRPCCall.amount_received_by_address(self,
                                                                          address=address,
                                                                          confirms=riskconstants.btc_risk_confirms['low']))

        if result >= expected_amount:
            log.info("received with 6 confirmed")
            log.info(result)
            log.info("low")
            return

        result = float(btc_rpc_call.BTCRPCCall.amount_received_by_address(self,
                                                                          address=address,
                                                                          confirms=riskconstants.btc_risk_confirms['medium']))

        if result >= expected_amount:
            log.info("received with 1 confirmed")
            log.info(result)
            log.info("medium")
            return

        result = float(btc_rpc_call.BTCRPCCall.amount_received_by_address(self,
                                                                          address=address,
                                                                          confirms=riskconstants.btc_risk_confirms['high']))

        if result >= expected_amount:
            log.info("received with 0 confirmed")
            log.info(result)
            log.info("high")
            return
        else:
            log.info("received amount is not enough")
            log.info(result)
            log.info("high")
