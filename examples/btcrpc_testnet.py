from bitcoinrpc.authproxy import AuthServiceProxy

btcRPCServer = "http://Ulysseys:8NzhGAbEXoJahLkPpNzmLxHqvQusgYVJWWx1J83y95gQ@127.0.0.1:18332"
access = AuthServiceProxy(btcRPCServer)
print access.getinfo()

print access.getreceivedbyaddress("mnNwwz8AMNLxVBAgrk31oVQb73vszYMzS8", 6)
