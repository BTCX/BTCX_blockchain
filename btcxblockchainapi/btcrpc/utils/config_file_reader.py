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

        servers = self.server_map[currency]
        receive = servers[wallet]
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
    
    def get_min_transfer_confirmations(self, currency):

        currency_config = self.server_map[currency]
        min_transfer_confirmations = currency_config['min_transfer_confirmations']
        return min_transfer_confirmations

    def get_min_transfer_amount(self, currency):

        currency_config = self.server_map[currency]
        min_transfer_amount = currency_config['min_transfer_amount']
        return min_transfer_amount

    def get_safe_address_to_be_transferred(self, currency):

        currency_config = self.server_map[currency]
        safe_address_to_be_transferred = currency_config['safe_address_to_be_transferred']
        return safe_address_to_be_transferred