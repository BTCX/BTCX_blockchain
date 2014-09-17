from btcrpc.utils.config_file_reader import ConfigFileReader
from btcrpc.utils.log import get_log
from django.test import TestCase
import yaml

__author__ = 'sikamedia'
__Date__ = '2014-09-17'

log = get_log("YAML test")
config_file = './btcxblockchainapi/config.yml'

class YAMLTestCase(TestCase):

    def setUp(self):
        server_config = open(config_file)
        self.server_map = yaml.safe_load(server_config)

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
