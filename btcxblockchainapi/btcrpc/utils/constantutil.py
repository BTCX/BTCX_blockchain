from btcrpc.utils.rpc_calls.rpc_call import RPCCall

def constant(f):
    def fset(self, value):
        raise SyntaxError
    def fget(self):
        return f(self)
    return property(fget, fset)


'''
def check_service_is_test_net(rpc_service):
    if isinstance(rpc_service, RPCCall):
        blockchain_info = rpc_service.get_blockchain_info()
        rpc_info = rpc_service.do_getinfo()
        return rpc_info["testnet"]
    else:
        raise TypeError("Expected object BTCRPCCall, got %s" % (type(rpc_service),))
'''


def check_service_chain(rpc_service):
    if isinstance(rpc_service, RPCCall):
        return rpc_service.get_chain()
    else:
        raise TypeError("Expected object python_bitcoinrpc, got %s" % (type(rpc_service),))


def check_for_failed_transactions(transaction_responses):
    transaction = \
          next((transaction for transaction in transaction_responses if transaction['status'] == 'fail'),
               None)
    return transaction is not None