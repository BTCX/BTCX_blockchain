from btcrpc.utils.constant_values import Constants
from btcrpc.utils.rpc_calls.bitcoin_cash_rpc import BitcoinCashRpc
from btcrpc.utils.rpc_calls.bitcoin_rpc import BitcoinRpc
from btcrpc.utils.rpc_calls.litecoin_rpc import LitecoinRpc
from btcrpc.utils.rpc_calls.python_bitcoinrpc import PythonBitcoinRpc
from btcrpc.utils.rpc_calls.python_ethjsonrpc import PythonEthJsonRpc


class RpcGenerator(object):
    @staticmethod
    def get_rpc_instance(wallet, currency):
        return {
            Constants.Currencies.BITCOIN: BitcoinRpc(wallet, currency),
            Constants.Currencies.BITCOIN_CASH: BitcoinCashRpc(wallet, currency),
            Constants.Currencies.LITECOIN: LitecoinRpc(wallet, currency),
            Constants.Currencies.ETHEREUM: PythonEthJsonRpc(wallet, currency)
        }.get(currency, PythonBitcoinRpc(wallet, currency))
