from account import CAccount


class CLimitedToken(CAccount):
    def __init__(self, DB, tokenName, totalSupply, creator, address):
        self.creator = 0
        super().__init__(DB, tokenName, address)
        if creator is None:
            pass
        else:
            self.totalSupply = totalSupply
            self.owner = creator
            self.owner.setAmount(self, totalSupply)
            self.setAmount(self, 0)
            self.chain.uniqueAccounts[creator.address] = creator

    def save(self, announce='Account;', who_is_signing=None):
        super().save(announce, who_is_signing)
        self.kade.save('limitedToken;' + self.address, [self.totalSupply, self.owner.address])

    def update(self):
        par = self.kade.get('limitedToken;' + self.address)

        _address = None
        if par is not None:
            self.totalSupply, _address = par

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

        if attacher is not None:
            account_1.chain.uniqueAccounts[account_2.address] = account_2
            account_2.chain.uniqueAccounts[account_1.address] = account_1
            return [attacher]

        raise Exception("Handshake", 'Handshake fails, no common connections')

    def spreadToWorld(self, accounts):
        for acc in accounts:
            acc.save()

    def attach(self, account, attacher):
        from actionToken import CActionToken

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

        account.setAmount(self, 0)
        self.chain.uniqueAccounts[account.address] = account
        account.chain.uniqueAccounts[self.address] = self

        listToSpread.append(self)
        listToSpread.append(attacher)
        listToSpread.append(account)
        self.spreadToWorld(listToSpread)

        return True
