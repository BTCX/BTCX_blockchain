from __future__ import absolute_import
import unittest
from ddt import ddt, data, file_data, unpack
from btcrpc.utils.config_file_reader_v2 import ConfigFileReader
from btcrpc.utils.log import get_log

log = get_log("YAML configuration file reader test")
config_file_reader_v2 = ConfigFileReader("/btcrpc/test/data/test_config_v2.yml")

try:
    import yaml
except ImportError:
    have_YAML_support = False
else:
    have_YAML_support = True
    del yaml

needs_yaml = unittest.skipUnless(
    have_YAML_support, "Need YAML to run this test"
)


class MyList(list):
    pass


def annotated(a, b):
    r = MyList([a, b])
    setattr(r, "__name__", "test_%d_greater_than_%d" % (a, b))
    return r

@ddt
class FooTestCase(unittest.TestCase):

    @data(annotated(2, 1), annotated(10, 5))
    def test_greater(self, value):
        a, b = value
        log.info( "%d, %d" % (a, b))
        self.assertGreater(a, b)

    @data((3, 2), (4, 3), (5, 3))
    @unpack
    def test_tuples_extracted_into_arguments(self, first_value, second_value):
        self.assertTrue(first_value > second_value)

    @needs_yaml
    @file_data("data/test_config_v2.yml")
    def test_config_v2_get_rpc_server_1(self, receive_1, receive_2, send_1):
        wallet_url = config_file_reader_v2.get_rpc_server("btc", "receive_1")
        log.info(wallet_url)
        data_wallet_url = receive_1['protocol'] + '://' + receive_1['username'] + ':' + receive_1['key'] + '@' + \
                           receive_1['host'] + ":" + str(receive_1['port'])
        log.info(data_wallet_url)
        self.assertEqual(wallet_url, data_wallet_url)

    @needs_yaml
    @file_data("data/test_config_v2.yml")
    def test_config_v2_get_rpc_server_2(self, receive_1, receive_2, send_1):
        wallet_url = config_file_reader_v2.get_rpc_server("btc", "receive_2")
        log.info(wallet_url)
        data_wallet_url = receive_2['protocol'] + '://' + receive_2['username'] + ':' + receive_2['key'] + '@' + \
                           receive_2['host'] + ":" + str(receive_2['port'])
        log.info(data_wallet_url)
        self.assertEqual(wallet_url, data_wallet_url)

    @needs_yaml
    @file_data("data/test_config_v2.yml")
    def test_config_v2_get_rpc_server_3(self, receive_1, receive_2, send_1):
        wallet_url = config_file_reader_v2.get_rpc_server("btc", "send_1")
        log.info(wallet_url)
        data_wallet_url = send_1['protocol'] + '://' + send_1['username'] + ':' + send_1['key'] + '@' + \
                           send_1['host'] + ":" + str(send_1['port'])
        log.info(data_wallet_url)
        self.assertEqual(wallet_url, data_wallet_url)

    @needs_yaml
    @file_data("data/test_config_v2.yml")
    def test_config_v2_get_wallet_list(self, receive_1, receive_2, send_1):
        # ['self', 'send_1', 'receive_2', 'receive_1']
        test_function_parameters = locals().keys()
        del test_function_parameters[0]
        wallets = config_file_reader_v2.get_wallet_list("btc")
        log.info(wallets)
        log.info(test_function_parameters)
        self.assertEqual(set(wallets), set(test_function_parameters))

    if __name__ == '__main__':
        unittest.main()