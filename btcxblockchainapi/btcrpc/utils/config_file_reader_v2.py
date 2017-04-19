import yaml
from singleton import Singleton
from btcxblockchainapi.settings import BASE_DIR

class ConfigFileReader(object):
    __metaclass__ = Singleton

    def __init__(self, relative_path="/btcxblockchainapi/config.yml"):
        print(BASE_DIR)
        print(BASE_DIR + relative_path)
        server_config = open(BASE_DIR + relative_path)
        self.server_map = yaml.safe_load(server_config)

    def get_rpc_server(self, currency, wallet):
        servers = self.server_map[currency]
        wallet_server = servers[wallet]
        username = wallet_server['username']
        key = wallet_server['key']
        protocol = wallet_server['protocol']
        host = wallet_server['host']
        port = wallet_server['port']
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