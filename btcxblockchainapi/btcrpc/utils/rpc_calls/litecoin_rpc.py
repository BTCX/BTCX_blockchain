from btcrpc.utils.rpc_calls.python_bitcoinrpc import PythonBitcoinRpc


class LitecoinRpc(PythonBitcoinRpc):
  def __init__(self, wallet, currency="bch"):
    super(LitecoinRpc, self).__init__(wallet=wallet, currency=currency)


  def set_tx_fee(self, amount):
    #Since we want to use the fee suggested by the node software, we don't make a RPC call to manually set the fee.
    return False