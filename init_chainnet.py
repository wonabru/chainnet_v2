from limitedToken import CLimitedToken
from database import CSQLLite
from actionToken import CActionToken
from wallet import CWallet
from baseAccount import CBaseAccount
from account import CAccount
from isolated_functions import *
import multiprocessing as mp
import time
import subprocess

class CInitChainnet:
    def __init__(self, main_wallet=None, password=None, from_scratch=False):

        self.tokens = {}
        self.wallet = CWallet(main_wallet, password, from_scratch=from_scratch)

        self.DB = CSQLLite()
        self.my_account = None
        self.my_accounts = {}
        self.update_my_accounts()
        self.set_my_account()
        self.load_tokens()

        #self.start_cloning()

    @staticmethod
    def loop_clone_kademlia(db):
        while True:
            db.clone_kademlia()
            print('Cloning finished')
            time.sleep(5)

    def start_cloning(self):

        process = mp.Process(target=self.loop_clone_kademlia, args=(self.DB, ))
        process.daemon = False
        process.start()
        process.join()
        pass

    def add_token(self, token, save=True):
        self.tokens[token.address] = token
        if save:
            self.DB.save('tokens', str(list(self.tokens.keys())))
            token.save()

        if self.DB.get('Account;' + token.address) is None:
            token.save()

    def get_token(self, address):
        return self.my_accounts[address]

    def get_token_by_name(self, name):

        for key, token in self.tokens.items():
            if token.accountName == name:
                return self.my_accounts[token.address]
        return None

    def set_my_account(self):

        self.my_account = CAccount(self.DB, 'main', self.wallet.pubKey)

        if self.DB.get('Account;' + self.my_account.address) is None:
            self.my_account.main_account = 1
            self.my_account.save()

        self.my_accounts[self.my_account.address] = self.my_account
        self.DB.save('my_main_accounts', str(list(set(self.my_accounts.keys()))))

    def get_tokens_addresses(self):
        _my_accounts = self.DB.get('tokens')
        if _my_accounts is None:
            _my_accounts = []
        else:
            _my_accounts = str2obj(_my_accounts)

        return _my_accounts

    def get_my_accounts(self):
        _my_accounts = self.DB.get('my_main_accounts')
        if _my_accounts is None:
            _my_accounts = list(self.my_accounts.keys())
        else:
            _my_accounts = str2obj(_my_accounts)

        return list(set(_my_accounts + self.get_tokens_addresses()))

    def select_my_account_by_name(self, name, update=True):

        if update:
            self.update_my_accounts()

        for add, acc in self.my_accounts.items():
            if acc.accountName == name:
                return acc
        return None

    def select_my_account_by_address(self, address, update=True):

        if update:
            self.update_my_accounts()

        for add, acc in self.my_accounts.items():
            if acc.address == address:
                return acc
        return None

    def load_tokens(self):
        _my_accounts = self.get_tokens_addresses()
        for acc in _my_accounts:
            try:
                _token = CLimitedToken(self.DB, '?', None, None, acc)
                _token.load_wallet()
                _token.update()
            except:
                _token = CActionToken(self.DB, '?', None, None, acc)
                _token.load_wallet()
                _token.update()

            if _token is not None:
                self.tokens[_token.address] = _token

        return True

    def get_my_accounts_names(self):
        names = []
        for acc in self.my_accounts:
            names.append(acc)
        return names

    def clear_announce(self, address, token):
        self.DB.clear('Lock;' + address, announce='Lock;')
        self.DB.clear('AtomicTransaction;' + address, announce='AtomicTransaction;')
        if address in token.isLocked and token.isLocked[address] in token.isLocked:
            del token.isLocked[token.isLocked[address]]
        if address in token.isLocked:
            del token.isLocked[address]
        token.save()

    def update_my_accounts(self):
        self.load_tokens()
        try:
            _my_accounts = self.get_my_accounts()
            for acc in _my_accounts:
                if acc in self.tokens.keys():

                    self.my_accounts[acc] = self.tokens[acc]
                else:
                    _account = CAccount(self.DB, '?', acc)
                    try:
                        _account.load_wallet()
                        _account.update()

                        self.my_accounts[_account.address] = _account
                    except Exception as ex:
                        showError(ex)

            _temp_my_main_account = self.select_my_account_by_name(self.my_account.accountName, update=False)
            self.my_account = _temp_my_main_account if _temp_my_main_account is not None else self.my_account

        except Exception as ex:
            print('No database found', str(ex))

