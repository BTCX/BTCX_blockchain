from abc import ABCMeta, abstractmethod

from btcrpc.utils.log import *

class RPCCall():
  __metaclass__ = ABCMeta

  @abstractmethod
  def do_getinfo(self):
    raise NotImplementedError

  @abstractmethod
  def do_get_new_address(self):
    raise NotImplementedError

  @abstractmethod
  def do_get_transaction(self, txid):
    raise NotImplementedError

  @abstractmethod
  def do_list_transactions(self, account, count=10, from_index=0):
    raise NotImplementedError

  @abstractmethod
  def amount_received_by_address(self, address="", confirms=0):
    raise NotImplementedError

  @abstractmethod
  def do_validate_address(self, address=""):
    raise NotImplementedError

  @abstractmethod
  def list_transactions(self, account="", count=10, from_index=0):
    raise NotImplementedError

  @abstractmethod
  def get_blockchain_info(self):
    raise NotImplementedError

  @abstractmethod
  def get_balance(self, minconf=1):
    raise NotImplementedError

  @abstractmethod
  def get_wallet_balance(self):
    raise NotImplementedError

  @abstractmethod
  def list_received_by_address(self, confirmations=1, include_empty=False):
    raise NotImplementedError

  @abstractmethod
  def set_tx_fee(self, amount):
    raise NotImplementedError

  @abstractmethod
  def send_to_address(self, address, amount, subtractfeefromamount=True):
    raise NotImplementedError

  @abstractmethod
  def send_many(self, minconf=1, **amounts):
    raise NotImplementedError
