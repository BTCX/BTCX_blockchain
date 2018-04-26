import yaml
from .singleton import Singleton
from btcrpc.utils.log import get_log, log_info, log_error

class ConfigFileReader(object, metaclass=Singleton):

    def __init__(self):
        server_config = open("./btcxblockchainapi/config_v2.yml")
        self.server_map = yaml.safe_load(server_config)
        self.log = get_log("Config file reader")

    def get_rpc_server(self, currency, wallet):
        servers = self.server_map[currency]
        wallet_server = servers[wallet]
        username = wallet_server['username']
        key = wallet_server['rpc_key']
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
        url_list.append(multiple_wallet_url + wallet_extension)
        url = ''.join(url_list)
        log_info(self.log, "Wallet extension to url is", multiple_wallet_url + wallet_extension)
        return url

    def get_wallet_list(self, currency):
        try:
            currency_config = self.server_map[currency]
            wallet_type_list = currency_config['wallet_types']
            wallet_list = []
            log_info(self.log, "Wallet type list to iterate over is", wallet_type_list)
            for walletType in wallet_type_list:
                log_info(self.log, "Wallet type", walletType)
                wallets = currency_config[str(walletType)]
                log_info(self.log, "Wallets", wallets)
                wallet_map = lambda wallet_name : {'wallet_name' : wallet_name, 'wallet_type' : walletType}
                wallet_jsons = list(map(wallet_map, wallets))
                log_info(self.log, "Wallet jsons to append", wallet_jsons)
                wallet_list.extend(wallet_jsons)
                log_info(self.log, "Wallet list after jsons has been appended", wallet_list)
            log_info(self.log, "Wallet list to return", wallet_list)
            return wallet_list
        except KeyError as e:
            log_error(self.log, "An Key error occurred during the get wallet list request, key entered", e)
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
        log_info(self.log, "Safe addresses config is", safe_config_addresses)
        log_info(self.log, "Safe address sent in is", safe_address)
        safe_address_matched_with_config = \
            next((currency_config[address] for address in safe_config_addresses if currency_config[address] == safe_address), None)
        if safe_address_matched_with_config:
            log_info(self.log, "The safe address sent in was part of the config safe addresses", None)
            return safe_address_matched_with_config
        else:
            log_error(
                self.log,
                "The safe address sent in was NOT part of the config safe addresses, Value error raised",
                None)
            raise ValueError("The address does not exist in the list of safe addresses")

    def get_reserved_fee_for_transferring(self, currency):
        currency_config = self.server_map[currency]
        fee = currency_config['reserved_fee']
        return fee

    def get_confirmations_mapping_to_risk(self, currency, risk):
        currency_config = self.server_map[currency]
        return currency_config['risk_confirmations'][risk]

    def get_private_key_encryption_password(self, currency, wallet):
        servers = self.server_map[currency]
        wallet_server = servers[wallet]
        return wallet_server['private_key_encryption_password']

    def get_api_key(self, api_key_service_name):
        api_keys = self.server_map['api_keys']
        return api_keys[api_key_service_name]

    def get_offsync_acceptance(self, currency):
        wallet_server = self.server_map[currency]
        return int(wallet_server['node_offsync_block_number_acceptance'])

    def get_request_time_limit(self):
        wallet_server = self.server_map['project_wide_values']
        return int(wallet_server['request_time_limit'])