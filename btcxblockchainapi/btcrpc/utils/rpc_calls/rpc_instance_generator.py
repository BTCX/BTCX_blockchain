from btcrpc.utils.rpc_calls.bitcoin_cash_rpc import BitcoinCashRpc
from btcrpc.utils.rpc_calls.bitcoin_rpc import BitcoinRpc
from btcrpc.utils.rpc_calls.litecoin_rpc import LitecoinRpc
from btcrpc.utils.rpc_calls.python_bitcoinrpc import PythonBitcoinRpc
from btcrpc.utils.rpc_calls.python_ethjsonrpc import PythonEthJsonRpc


class RpcGenerator(object):
    @staticmethod
    def get_rpc_instance(wallet, currency):
        return {
            'btc': BitcoinRpc(wallet, currency),
            'bch': BitcoinCashRpc(wallet, currency),
            'ltc': LitecoinRpc(wallet, currency),
            'eth': PythonEthJsonRpc(wallet, currency)
        }.get(currency, PythonBitcoinRpc(wallet, currency))
