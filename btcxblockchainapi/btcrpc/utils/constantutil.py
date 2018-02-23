from btcrpc.utils.rpc_calls.rpc_call import RPCCall

def constant(f):
    def fset(self, value):
        raise SyntaxError
    def fget(self):
        return f(self)
    return property(fget, fset)


def check_service_is_test_net(rpc_service):
    if isinstance(rpc_service, RPCCall):
        rpc_info = rpc_service.do_getinfo()
        return rpc_info["testnet"]
    else:
        raise TypeError("Expected object BTCRPCCall, got %s" % (type(rpc_service),))
