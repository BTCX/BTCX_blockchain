from btcrpc.utils.rpc_calls.bitcoin_cash_rpc import BitcoinCashRpc
from btcrpc.utils.rpc_calls.bitcoin_rpc import BitcoinRpc
from btcrpc.utils.rpc_calls.litecoin_rpc import LitecoinRpc
from btcrpc.utils.rpc_calls.python_bitcoinrpc import PythonBitcoinRpc

class RpcGenerator(object):
  @staticmethod
  def get_rpc_instance(wallet, currency):
    if currency == 'btc':
      return BitcoinRpc(wallet, currency)
    elif currency == 'bch':
      return BitcoinCashRpc(wallet, currency)
    elif currency == 'ltc':
      return LitecoinRpc(wallet, currency)
    else:
      return PythonBitcoinRpc(wallet, currency)

    #Removed code that creates an instance of every rpc instance.
    # return {
    #   'btc': BitcoinRpc(wallet,currency),
    #   'bch': BitcoinCashRpc(wallet,currency),
    #   'ltc': LitecoinRpc(wallet,currency)
    # }.get(currency, PythonBitcoinRpc(wallet,currency))
