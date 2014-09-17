import yaml

__author__ = 'sikamedia'
__Date__ = '2014-09-17'


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ConfigFileReader():
    __metaclass__ = Singleton

    def __init__(self):
        server_config = open("./btcxblockchainapi/config.yml")
        self.server_map = yaml.safe_load(server_config)

    def get_rpc_server(self, currency, wallet):

        btc_servers = self.server_map[currency]
        receive = btc_servers[wallet]
        username = receive['username']
        key = receive['key']
        protocol = receive['protocol']
        host = receive['host']
        port = receive['port']
        url_list = list()
        url_list.append(protocol)
        url_list.append('://')
        url_list.append(username)
        url_list.append(':')
        url_list.append(key)
        url_list.append('@')
        url_list.append(host)
        url_list.append(':')
        url_list.append(str(port))
        url = ''.join(url_list)
        return url
