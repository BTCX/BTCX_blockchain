from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.log import get_log
from django.test import TestCase
import yaml

__author__ = 'sikamedia'
__Date__ = '2014-09-17'

log = get_log("YAML test")
config_file = './btcxblockchainapi/config.yml'
risk_low_confirmations = 6
risk_medium_confirmations = 1
risk_high_confirmations = 0


class YAMLTestCase(TestCase):

    def setUp(self):
        server_config = open(config_file)
        self.server_map = yaml.safe_load(server_config)
        self.yml_config = ConfigFileReader()

    def test_read_yml(self):

        log.info(self.server_map)
        expect_url = "http://bitcoinrpc:6CuNvnTogKqCqCA9SKrr3XBDNCPt6gVThUxUAnGWawve@127.0.0.1:18332"
        btc_servers = self.server_map['btc']
        receive = btc_servers['receive']
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
        log.info(url)
        self.assertEquals(url, expect_url)

    def test_singleton_yml_reader(self):

        yml_reader_send = ConfigFileReader()
        send_url = yml_reader_send.get_rpc_server(currency='btc', wallet='send')
        log.info(send_url)
        yml_reader_receive = ConfigFileReader()
        receive_url = yml_reader_receive.get_rpc_server(currency='btc', wallet='receive')
        log.info(receive_url)
        self.assertEqual(id(yml_reader_send), id(yml_reader_receive))

    def test_get_min_transfer_confirmations(self):
        min_transfer_confirmations = self.yml_config.get_min_transfer_confirmations(currency='btc')
        log.info('Minimum transfer confirmations : %d' % min_transfer_confirmations)

    def test_get_min_transfer_amount(self):
        min_transfer_amount = self.yml_config.get_min_transfer_amount(currency='btc')
        log.info('Minimum transfer amount : %f' % min_transfer_amount)

    def test_get_safe_address_to_be_transferred(self):
        safe_address_to_be_transferred = self.yml_config.get_safe_address_to_be_transferred(currency='btc')
        log.info('Safe address to be transferred : %s' % safe_address_to_be_transferred)

    def test_get_risk_confirmations_low(self):
        risk_low_confirmations_from_config = self.yml_config.get_confirmations_mapping_to_risk(currency='btc',
                                                                                               risk='low')
        self.assertEqual(risk_low_confirmations, risk_low_confirmations_from_config)

    def test_get_risk_confirmations_medium(self):
        risk_low_confirmations_from_config = self.yml_config.get_confirmations_mapping_to_risk(currency='btc',
                                                                                               risk='medium')
        self.assertEqual(risk_medium_confirmations, risk_low_confirmations_from_config)

    def test_get_risk_confirmations_high(self):
        risk_low_confirmations_from_config = self.yml_config.get_confirmations_mapping_to_risk(currency='btc',
                                                                                               risk='high')
        self.assertEqual(risk_high_confirmations, risk_low_confirmations_from_config)