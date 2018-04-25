from enum import IntEnum

class ChainEnum(IntEnum):
  UNKNOWN = 0
  MAIN = 1
  TEST_NET = 2
  REGTEST = 3

  def get_int_value(self):
    return int(self.value)