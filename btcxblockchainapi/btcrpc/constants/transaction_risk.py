__author__ = 'sikamedia'
__Date__ = '2015-01-19'

from btcrpc.utils.config_file_reader import ConfigFileReader


yml_config = ConfigFileReader()

risk_low_confirmations = yml_config.get_confirmations_mapping_to_risk(currency='btc', risk='low')
risk_medium_confirmations = yml_config.get_confirmations_mapping_to_risk(currency='btc', risk='medium')
risk_high_confirmations = yml_config.get_confirmations_mapping_to_risk(currency='btc', risk='high')