from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.rpc_calls.rpc_call import RPCCall
from btcrpc.utils.chain_enum import ChainEnum
import json
import socket
import logging


log = logging.getLogger("PythonBitcoinRpc Call:")


class PythonBitcoinRpc(RPCCall):
  def __init__(self, wallet, currency):
    yml_config_reader = ConfigFileReader()
    url = yml_config_reader.get_rpc_server(currency=currency, wallet=wallet)
    self.access = AuthServiceProxy(url)

  def do_getinfo(self):
    return self.access.getwalletinfo()

  def do_get_new_address(self):
    return self.access.getnewaddress()

  def do_get_transaction(self, txid):
    try:
      return self.access.gettransaction(txid)
    except RuntimeError:
      # return simplejson.dumps ({u'error' : u'txid is not valid'})
      return None

  def do_list_transactions(self, account, count=10, from_index=0):
    try:
      return self.access.listtransactions(account, count, from_index)
    except RuntimeError:
      print("calling failure")

  def amount_received_by_address(self, address="", confirms=0):
    return self.access.getreceivedbyaddress(address, confirms)

  def do_validate_address(self, address=""):
    validate_res = self.access.validateaddress(address)
    address_info_res = self.access.getaddressinfo(address)
    validate_res.update(address_info_res)
    return validate_res

  def do_bump_fee(self, txid, **options):
    return self.access.bumpfee(txid, **options)

  def do_estimate_smart_fee(self, conf_target, *estimate_mode):
    return self.access.estimatesmartfee(conf_target, *estimate_mode)

  def list_transactions(self, account="", count=10, from_index=0):
    return self.access.listtransactions(account, count, from_index)

  def get_blockchain_info(self):
    return self.access.getblockchaininfo()

  def get_balance(self, minconf=1):
    return self.access.getbalance("*", minconf)

  def get_wallet_balance(self):
    return self.access.getbalance()

  def get_unconfirmed_balance(self):
    return self.access.getunconfirmedbalance()

  def get_chain(self):
    blockchain_info = self.get_blockchain_info()
    if blockchain_info["chain"] == "main":
      return ChainEnum.MAIN
    elif blockchain_info["chain"] == "test":
      return ChainEnum.TEST_NET
    elif blockchain_info["chain"] == "regtest":
      return ChainEnum.REGTEST
    else:
      return ChainEnum.UNKNOWN

  def list_received_by_address(self, address, confirmations=0, include_empty=False, include_watchonly=False):
    return self.access.listreceivedbyaddress(confirmations, include_empty, include_watchonly, address)

  def set_tx_fee(self, amount):
    return self.access.settxfee(amount)

  def send_to_address(self, address, amount, subtractfeefromamount=True):
    return self.access.sendtoaddress(address, amount, "", "", subtractfeefromamount)

  # amount is type of dictionary
  def send_many(self, minconf=1, **amounts):
    log.info("sendmany to: %s", json.dumps(amounts))
    amounts_string = json.dumps(amounts['amounts'])
    amounts_object = json.loads(amounts_string)
    try:
      return True, self.access.sendmany("", amounts_object, minconf)
    except JSONRPCException as ex:
      return False, ex
    except socket.error as e:
      return False, e
