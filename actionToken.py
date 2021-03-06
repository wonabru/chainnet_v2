import operator
from account import CAccount


class CActionToken(CAccount):
    def __init__(self, DB, tokenName, initialSupply, creator, address):
        self.creator = 0
        super().__init__(DB, tokenName, address)
        self.minAmount = 10 ** -self.decimalPlace
        if creator is None:
            pass
        else:
            self.totalSupply = initialSupply
            self.owner = creator
            self.owner.setAmount(self, initialSupply)
            self.setAmount(self, 0)
            self.chain.uniqueAccounts[creator.address] = creator


    def save(self, announce='Account;', who_is_signing=None):
        super().save(announce, who_is_signing)
        self.kade.save('actionToken;' + self.address, [self.totalSupply, self.owner.address])

    def update(self):
        par = self.kade.get('actionToken;' + self.address)
        _address = None
        if par is not None:
            self.totalSupply, _address = par
        self.minAmount = 10 ** -self.decimalPlace

        super().update()

        if _address is not None:
            _account = CAccount(self.kade, '?', _address)
            _account.update()
            self.owner = _account

    def showAll(self):
        #self.update()
        totalSupply = 0
        for acc in self.chain.uniqueAccounts:

            self.chain.uniqueAccounts[acc].show()
            totalSupply = totalSupply + self.chain.uniqueAccounts[acc].amount[self.address] \
            if self.address in self.chain.uniqueAccounts[acc].amount.keys() else totalSupply
        
        ret = self.accountName + ' total Supply: ' + str(self.totalSupply) + ' and on all accounts: ' + str(totalSupply)
        return ret

    def handshake(self, account_1, account_2, attacher):
        
        list1 = account_1.chain.uniqueAccounts
        list2 = account_2.chain.uniqueAccounts

        '''
        account = None
        for key, value in list1.items():
            if key in list2:
                account = value
                break
        '''

        if attacher is not None:
            account_1.chain.uniqueAccounts[account_2.address] = account_2
            account_2.chain.uniqueAccounts[account_1.address] = account_1
            #awarded should be oldest connection binding two accounts
            attacher.addAmount(self, self.minAmount)
            self.totalSupply += self.minAmount
            return [attacher]
        
        raise Exception("Handshake", 'Handshake fails, no common connections')
    
    def spreadToWorld(self, accounts):
        #self.update()
        for acc in accounts:
            acc.save()
                
    def attach(self, account, attacher):
        from limitedToken import CLimitedToken

        if account is None:
            raise Exception("Attach", "No account exists with given name ")

        if isinstance(account, CLimitedToken) or isinstance(account, CActionToken):
            raise Exception("Attach", "Attached account cannot be any Token.")

        if account.address in self.chain.uniqueAccounts:
            raise Exception("Attach", "Account is just attached.")

        if self.address == account.address:
            raise Exception("Attach", "Account cannot be attached to itself.")

        listToSpread = self.handshake(self, account, attacher)

        if listToSpread is None:
            raise Exception("Attach", "Nothing to attach")

        if attacher.address == listToSpread[0].address:
            attacher = listToSpread[0]
            listToSpread.remove(attacher)

        if attacher.address not in self.chain.accountsCreated.keys():
            self.chain.accountsCreated[attacher.address] = 1
        else:
            self.chain.accountsCreated[attacher.address] += 1
        
        noCreated = self.chain.accountsCreated[attacher.address] - 1
        
        if attacher.addAmount(self, -(self.minAmount * noCreated)) == False:
            self.chain.accountsCreated[attacher.address] -= 1
            raise Exception("Attach", "Not enough funds on " + attacher.accountName + ". It is needed "+str(self.minAmount * noCreated)+" [ "+self.accountName+" ] ")
        
        self.totalSupply -= (self.minAmount * noCreated)
        account.setAmount(self, 0)
        self.chain.uniqueAccounts[account.address] = account
        account.chain.uniqueAccounts[self.address] = self
        
        sorted_pubKey = sorted(self.chain.uniqueAccounts.items(), key=operator.itemgetter(0))
        index_account = sorted_pubKey.index((account.address, account)) - 1
        
        dad = sorted_pubKey[index_account][1]
        dad.addAmount(self, self.minAmount)
        self.totalSupply += self.minAmount

        listToSpread.append(attacher)
        listToSpread.append(self)
        listToSpread.append(account)

        if dad.address == listToSpread[0].address:
            listToSpread[0] = dad
        else:
            listToSpread.append(dad)

        self.spreadToWorld(listToSpread)
        
        return True
