from baseAccount import CBaseAccount
from atomicTransaction import check_if_my_connection



class CAccount(CBaseAccount):
    def __init__(self, DB, accountName, address):
        self.kade = DB
        super().__init__(DB, accountName, address)
        self.chain.uniqueAccounts = {}

    def invite(self, accountName, creator, address):

        account = CAccount(self.kade, accountName, address)
        account.update()
        check_if_my_connection(self, creator)
        self.chain.uniqueAccounts[address] = account
        account.chain.uniqueAccounts[self.address] = self
        account.save(announce='Account;')
        self.save()
        return account

    def save(self, announce='Account;', who_is_signing=None):
        #self.update()
        super().save(announce, who_is_signing=who_is_signing)
        
    def update(self, deep=True):
        super().update(deep)

