from django.test import TestCase
from btcrpc import btcrpcall
from btcrpc.utils import timeUtil, jsonutil
#import simplejson as json
import simplejson

class BTCRPCTestCase(TestCase):
    def setUp(self):
        self.btcRPCcall = btcrpcall.BTCRPCall()

    
    def test_epochtime_to_datetime(self):
        epoch_time = timeUtil.TimeUtils.epoch_to_datetime(1347517119)
        print epoch_time
        self.assertEquals(epoch_time, '2012-09-13 06:18:39')

    def test_address_receive_btc(self):
        transactions_log = self.btcRPCcall.do_list_transactions("n4LSoNto3TobC6ToxstxRXT3V9TpZa1ydi")     
        #print transactions_log["account"]
        #print jsonutil.JsonUtils.is_json(transactions_log)
        
        transactions_log_json = simplejson.dumps(transactions_log, use_decimal=True)
        print transactions_log_json

        print jsonutil.JsonUtils.is_json(transactions_log_json)        

        

        #object = simplejson.loads(transactions_log)
        print transactions_log[0]
        
        for o in transactions_log:
            print o["amount"]
            print o["address"]
            print o["txid"]
            print timeUtil.TimeUtils.epoch_to_datetime(o["timereceived"])
            print timeUtil.TimeUtils.epoch_to_datetime(o["blocktime"])
            print o["confirmations"]
    def test_address_receive_btc_with_txid(self):
        pass 
