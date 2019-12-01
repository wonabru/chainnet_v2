from limitedToken import CLimitedToken
from database import CSQLLite
from actionToken import CActionToken
from wallet import CWallet
from baseAccount import CBaseAccount
from account import CAccount
from isolated_functions import *


class CInitChainnet:
	def __init__(self, main_wallet=None, password=None, from_scratch=False):

		self.tokens = {}
		self.my_accounts_names = {}
		self.wallet = CWallet(main_wallet, password, from_scratch=from_scratch)
		self.DB = CSQLLite()

		self.my_accounts = {}
		self.set_my_account()
		self.load_tokens()

	def add_token(self, token, save=True):
		self.tokens[token.address] = token
		if save:
			self.DB.save('tokens', str(list(self.tokens.keys())))
			token.owner.save()
			token.save()

		if self.DB.get('Account:' + token.address) is None:
			token.save()

	def get_token(self, address):
		return self.tokens[address]

	def get_token_by_name(self, name):

		for key, token in self.tokens.items():
			if token.accountName == name:
				return token
		return None

	def set_my_account(self):

		self.my_account = CAccount(self.DB, '@main', self.wallet.pubKey)

		if self.DB.get('Account:' + self.my_account.address) is None:
			self.my_account.main_account = 1
			self.my_account.save()

		self.my_accounts[self.my_account.address] = self.my_account
		self.DB.save('my_main_accounts', str(list(set(self.my_accounts.keys()))))

	def get_external_addresses(self):

		_external_accounts = self.DB.get('EXTERNAL')

		if _external_accounts is not None:
			return _external_accounts
		else:
			return []

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

		return list(set(_my_accounts + self.get_external_addresses() + self.get_tokens_addresses()))

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
		return self.my_accounts_names.values()


	def update_my_accounts(self):
		self.load_tokens()
		try:
			_my_accounts = self.get_my_accounts()
			for acc in _my_accounts:
				if acc in self.tokens.keys():

					self.my_accounts[acc] = self.tokens[acc]
					self.my_accounts_names[acc] = self.tokens[acc].accountName
				else:
					_account = CAccount(self.DB, '?', acc)
					try:
						_account.load_wallet()
						_account.update()

						self.my_accounts[_account.address] = _account
						self.my_accounts_names[_account.address] = _account.accountName
					except Exception as ex:
						showError(ex)

			_temp_my_main_account = self.select_my_account_by_name(self.my_account.accountName, update=False)
			self.my_account = _temp_my_main_account if _temp_my_main_account is not None else self.my_account
		except Exception as ex:
			print('No database found', str(ex))
