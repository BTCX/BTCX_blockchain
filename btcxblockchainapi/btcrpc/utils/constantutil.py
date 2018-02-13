from btcrpc.utils.btc_rpc_call import BTCRPCCall

def constant(f):
    def fset(self, value):
        raise SyntaxError
    def fget(self):
        return f(self)
    return property(fget, fset)


def check_service_is_test_net(btc_service):
    print("in service")
    if isinstance(btc_service, BTCRPCCall):
        print("in if")
        print("before")
        btc_info = btc_service.do_getinfo()
        print("after")
        print(btc_info)
        return btc_info["testnet"]
    else:
        print("in else")
        raise TypeError("Expected object BTCRPCCall, got %s" % (type(btc_service),))
