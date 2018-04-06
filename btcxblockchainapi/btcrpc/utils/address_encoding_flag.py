from enum import Enum, auto


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

#If we want to use the number in the enum order as the value instead, replace inheritance from AutoName to Enum.
class AddressEncodingFlag(AutoName):
  NO_SPECIFIC_ENCODING = auto()
  ETHEREUM_CHECKSUM_ADDRESS = auto()