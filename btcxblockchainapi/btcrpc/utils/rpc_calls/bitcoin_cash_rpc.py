from btcrpc.utils.rpc_calls.python_bitcoinrpc import PythonBitcoinRpc


class BitcoinCashRpc(PythonBitcoinRpc):
  def __init__(self, wallet, currency="bch"):
    super(BitcoinCashRpc, self).__init__(wallet=wallet, currency=currency)