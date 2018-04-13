from abc import ABCMeta, abstractmethod
from btcrpc.utils.address_encoding_flag import AddressEncodingFlag

from btcrpc.utils.log import *

class RPCCall():
    __metaclass__ = ABCMeta

    @abstractmethod
    def amount_received_by_address(self, address="", confirms=0):
        raise NotImplementedError

    @abstractmethod
    def do_getinfo(self):
        raise NotImplementedError

    @abstractmethod
    def do_get_new_address(self, wallet):
        raise NotImplementedError

    @abstractmethod
    def do_set_account(self, address, account):
        raise NotImplementedError

    @abstractmethod
    def do_get_transaction(self, txid):
        raise NotImplementedError

    @abstractmethod
    def do_list_transactions(self, account, count=10, from_index=0):
        raise NotImplementedError

    @abstractmethod
    def do_validate_address(self, address=""):
        raise NotImplementedError

    @abstractmethod
    def encode_address(self, address, encoding_flag=AddressEncodingFlag.NO_SPECIFIC_ENCODING):
        raise NotImplementedError

    @abstractmethod
    def list_transactions(self, account="", count=10, from_index=0):
        raise NotImplementedError

    @abstractmethod
    def send_from(self, from_account="", to_address="", amount=0, minconf=1):
        raise NotImplementedError

    @abstractmethod
    def get_blockchain_info(self):
        raise NotImplementedError

    @abstractmethod
    def get_received_amount_by_account(self, account="", minconf=1):
        raise NotImplementedError

    @abstractmethod
    def get_balance(self, account="", minconf=1):
        raise NotImplementedError

    @abstractmethod
    def get_wallet_balance(self):
        raise NotImplementedError

    @abstractmethod
    def move(self, from_account="", to_account="", amount=0, minconf=1):
        raise NotImplementedError

    @abstractmethod
    def list_accounts(self, confirmations=1):
        raise NotImplementedError

    @abstractmethod
    def list_received_by_address(self, confirmations=1, include_empty=False):
        raise NotImplementedError

    @abstractmethod
    def get_addresses_by_account(self, account):
        raise NotImplementedError

    @abstractmethod
    def set_tx_fee(self, amount):
        raise NotImplementedError

    @abstractmethod
    def send_to_address(self, address, amount, subtractfeefromamount=True, from_wallet=''):
        raise NotImplementedError

    @abstractmethod
    def send_many(self, from_account="", minconf=1, from_wallet="", **amounts):
        raise NotImplementedError
