from btcrpc.utils.rpc_calls.python_bitcoinrpc import PythonBitcoinRpc


class BitcoinRpc(PythonBitcoinRpc):
  def __init__(self, wallet, currency="btc"):
    super(BitcoinRpc, self).__init__(wallet, currency)