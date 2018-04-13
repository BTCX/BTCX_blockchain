
class GetAccountIterator(object):
    def __init__(self, accounts = []):
        self.accounts = accounts
        self.current_account_index = 0
        self.accounts_list_length = len(accounts)
        self.balance_dict = {}

    ''' The idea with this function is to get the next account in the list that has real balance on it that will not 
        lead to a double spend. If no account has any balance left, we return None. if the __iter function is implemented
        to support iteration over the class object, the object returned by this function is the one that should be 
        returned.'''
    def get_next_suitable_account(self):
        if self.current_account_index >= len(self.accounts):
            return None

        if not self.has_balance_set_for_account(self.accounts[self.current_account_index]):
            return self.accounts[self.current_account_index]
        else:
            account_balance = self.get_balance_of_account(self.accounts[self.current_account_index])
            if account_balance > 0:
                return self.accounts[self.current_account_index]
            else:
                self.current_account_index += 1
                return self.get_next_suitable_account()

    def get_balance_of_account(self, account):
        return self.balance_dict[account] if self.has_balance_set_for_account(account) else 0

    def set_balance_of_account(self, account, balance):
        self.balance_dict[account] = balance

    def has_balance_set_for_account(self, account):
        return account in self.balance_dict

    def increase_account_index(self):
        self.current_account_index += 1