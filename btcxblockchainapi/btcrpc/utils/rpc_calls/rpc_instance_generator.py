from btcrpc.utils.constant_values import Constants
from btcrpc.utils.rpc_calls.bitcoin_cash_rpc import BitcoinCashRpc
from btcrpc.utils.rpc_calls.bitcoin_rpc import BitcoinRpc
from btcrpc.utils.rpc_calls.litecoin_rpc import LitecoinRpc
from btcrpc.utils.rpc_calls.python_bitcoinrpc import PythonBitcoinRpc
from btcrpc.utils.rpc_calls.python_ethjsonrpc import PythonEthJsonRpc
from btcrpc.utils.endpoint_timer import EndpointTimer


class RpcGenerator(object):
    @staticmethod
    def get_rpc_instance(wallet, currency, endpoint_timer=None):
        if not endpoint_timer:
            endpoint_timer = EndpointTimer()
        if currency == Constants.Currencies.BITCOIN:
            return BitcoinRpc(wallet, currency)
        elif currency == Constants.Currencies.BITCOIN_CASH:
            return BitcoinCashRpc(wallet, currency)
        elif currency == Constants.Currencies.LITECOIN:
            return LitecoinRpc(wallet, currency)
        elif currency == Constants.Currencies.ETHEREUM:
            return PythonEthJsonRpc(wallet, currency, endpoint_timer)
        else:
            raise TypeError("Incorrect currency entered")

        #This way to return the correct rpc instance was removed as it creates an instance of all of them.
        # return {
        #     Constants.Currencies.BITCOIN: BitcoinRpc(wallet, currency),
        #     Constants.Currencies.BITCOIN_CASH: BitcoinCashRpc(wallet, currency),
        #     Constants.Currencies.LITECOIN: LitecoinRpc(wallet, currency),
        #     Constants.Currencies.ETHEREUM: PythonEthJsonRpc(wallet, currency)
        # }.get(currency, PythonBitcoinRpc(wallet, currency))
