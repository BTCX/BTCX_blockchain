from bitcoinrpc.authproxy import AuthServiceProxy

btcRPCServer = "http://Ulysseys:8NzhGAbEXoJahLkPpNzmLxHqvQusgYVJWWx1J83y95gQ@127.0.0.1:8332"
access = AuthServiceProxy(btcRPCServer)
print access.getinfo()
