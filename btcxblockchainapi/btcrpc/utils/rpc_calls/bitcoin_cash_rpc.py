from btcrpc.utils.rpc_calls.python_bitcoinrpc import PythonBitcoinRpc


class BitcoinCashRpc(PythonBitcoinRpc):
  def __init__(self, wallet, currency="bch"):
    super(BitcoinCashRpc, self).__init__(wallet=wallet, currency=currency)

  def set_tx_fee(self, amount):
    #Since we want to use the fee suggested by the node software, we don't make a RPC call to manually set the fee.
    return True

  def do_validate_address(self, address=""):
    if(address.startswith("bchtest") or address.startswith("bitcoincash")):
      return self.access.validateaddress(address)
    else:
      return {"isvalid": False}