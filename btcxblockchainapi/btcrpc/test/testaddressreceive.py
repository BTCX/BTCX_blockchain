from django.test import TestCase
from btcrpc import btcrpcall
from btcrpc.utils.timeUtil import TimeUtils
from btcrpc.utils.jsonutil import JsonUtils
import simplejson
from btcrpc.log import *
from btcrpc.vo.api_output_result import AddressReceiveOutputAttributeConst

log = get_log("test_address_receive")

class BTCRPCTestCase(TestCase):

    def setUp(self):
        self.btcRPCcall = btcrpcall.BTCRPCall()

    
    def test_epochtime_to_datetime(self):
        epoch_time = TimeUtils.epoch_to_datetime(1347517119)
        print epoch_time
        self.assertEquals(epoch_time, '2012-09-13 06:18:39')

    def test_address_receive_btc(self):
        transactions_log = self.btcRPCcall.do_list_transactions("n4LSoNto3TobC6ToxstxRXT3V9TpZa1ydi")     
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

    def test_address_receive_btc_with_txid(self):
        transactions_log  = self.btcRPCcall.do_get_transaction("61b34a7c10ddd9f278207b44c5635440c85f5fa082fcf2d440f8b763a3659649")
        transactions_log_json = simplejson.dumps(transactions_log, use_decimal=True)

        log.info(transactions_log_json)

        attributeConst = AddressReceiveOutputAttributeConst()
        log.info(transactions_log[attributeConst.TXID])
        log.info(transactions_log[attributeConst.AMOUNT])
        log.info(transactions_log["details"][0][attributeConst.ADDRESS])
        log.info(TimeUtils.epoch_to_datetime(transactions_log[attributeConst.TIMERECEIVED]))
        log.info(TimeUtils.epoch_to_datetime(transactions_log[attributeConst.BLOCKTIME]))
          
    
