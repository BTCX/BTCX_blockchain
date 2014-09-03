from btcrpc.btc_rpc_call import BTCRPCCall

def constant(f):
    def fset(self, value):
        raise SyntaxError
    def fget(self):
        return f(self)
    return property(fget, fset)


def check_service_is_test_net(btc_service):
    if isinstance(btc_service, BTCRPCCall):
        btc_info = btc_service.do_getinfo()
        return btc_info["testnet"]
    else:
        raise TypeError("Expected object BTCRPCCall, got %s" % (type(btc_service),))
