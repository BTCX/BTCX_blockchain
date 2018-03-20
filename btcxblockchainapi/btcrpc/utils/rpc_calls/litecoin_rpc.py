from btcrpc.utils.rpc_calls.python_bitcoinrpc import PythonBitcoinRpc


class LitecoinRpc(PythonBitcoinRpc):
  def __init__(self, wallet, currency="bch"):
    super(LitecoinRpc, self).__init__(wallet=wallet, currency=currency)