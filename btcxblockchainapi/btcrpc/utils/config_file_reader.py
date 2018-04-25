import yaml
from .singleton import Singleton

class ConfigFileReader(object, metaclass=Singleton):

    def __init__(self):
        server_config = open("./btcxblockchainapi/config.yml")
        self.server_map = yaml.safe_load(server_config)

    def get_rpc_server(self, currency, wallet):
        servers = self.server_map[currency]
        wallet_server = servers[wallet]
        username = wallet_server['username']
        key = wallet_server['key']
        protocol = wallet_server['protocol']
        host = wallet_server['host']
        port = wallet_server['port']
        wallet_extension = wallet_server['wallet_url_extension']
        multiple_wallet_url = servers['multiple_wallet_url']
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
        if len(wallet_extension) > 0:
            url_list.append(multiple_wallet_url + wallet_extension)
        url = ''.join(url_list)
        return url

    def get_wallet_list(self, currency):
        try:
            currency_config = self.server_map[currency]
            wallet_type_list = currency_config['wallet_types']
            wallet_list = []
            for walletType in wallet_type_list:
                wallets = currency_config[str(walletType)]
                wallet_map = lambda wallet_name : {'wallet_name' : wallet_name, 'wallet_type' : walletType}
                wallet_jsons = list(map(wallet_map, wallets))
                wallet_list.extend(wallet_jsons)
            return wallet_list
        except KeyError as e:
            return []
    
    def get_min_transfer_confirmations(self, currency):

        currency_config = self.server_map[currency]
        min_transfer_confirmations = currency_config['min_transfer_confirmations']
        return min_transfer_confirmations

    def get_min_transfer_amount(self, currency):

        currency_config = self.server_map[currency]
        min_transfer_amount = currency_config['min_transfer_amount']
        return min_transfer_amount

    def get_safe_address_to_be_transferred(self, currency, safe_address):
        currency_config = self.server_map[currency]
        safe_config_addresses = currency_config['safe_addresses']
        safe_address_matched_with_config = \
            next((currency_config[address] for address in safe_config_addresses if currency_config[address] == safe_address), None)
        if safe_address_matched_with_config:
            return safe_address_matched_with_config
        else:
            raise ValueError("The address does not exist in the list of safe addresses")

    def get_reserved_fee_for_transferring(self, currency):
        currency_config = self.server_map[currency]
        fee = currency_config['reserved_fee']
        return fee

    def get_confirmations_mapping_to_risk(self, currency, risk):
        currency_config = self.server_map[currency]
        return currency_config['risk_confirmations'][risk]