import numpy as np
import datetime as dt
from chain import CChain
from wallet import CWallet
from transaction import CTransaction, CAtomicTransaction
from isolated_functions import *


class CBaseAccount:
    def __init__(self, DB, accountName, address):
        self.kade = DB
        self.decimalPlace = 2
        self.amount = {}
        self.address = address
        self.accountName = accountName
        self.chain = CChain()
        self.isLocked = {}
        self.wallet = None
        self.main_account = 0
        self.password = ''

    def setAmount(self, token, amount):
        if amount < 0:
            raise Exception('set amount error', 'Amount of tokens cannot be less than zero')
        print('Account: ', self.accountName, ' is setting amount ', amount, ' [ ', token.accountName, ' ] ')
        self.amount[token.address] = np.round(amount, self.decimalPlace)

        return True

    def addAmount(self, token, amount):

        if token.address not in self.amount.keys():
            self.setAmount(token, 0)
            print('Warning: there was no set any initial amount. Set to 0')

        temp_amount = self.amount[token.address] + amount
        if temp_amount < 0:
            print('not enough funds')
            return False
        return self.setAmount(token, temp_amount)

    def load_base_account(self, address):
        try:
            _account = CBaseAccount(self.kade, '?', address)
            _account.update()
        except Exception as ex:
            raise Exception('Load base account', str(ex))

        return  _account

    def lockAccounts(self, my_account, signature1, account2address, time_to_close):

        if CWallet().verify('Locking for deal; ' + my_account.address + ' + ' +
                            account2address + ' with ' + self.address + ' till ' + str(time_to_close),
                            signature1, my_account.address):
            self.isLocked[my_account.address] = account2address
        else:
            raise Exception('Lock Accounts fails. Signature not valid for account ' +
                            my_account.accountName, 'Locking for deal fails; ' + my_account.address + ' + ' +
                            account2address + ' till ' + str(time_to_close))

        #save means announce to World
        self.save_lock(key='Lock;' + account2address, value='Lock;' + account2address + ';' + my_account.address + ';' + self.address +
                           ';' + str(time_to_close))

    def lock_loop(self, my_account, account2address, time_to_close, finish):

        self.save_lock(key='Lock;' + account2address, value='Lock;' + account2address + ';' + my_account.address + ';' + self.address +
                           ';' + str(time_to_close))
        _par = self.kade.look_at('Lock;' + my_account.address)
        if _par is not None:
            _par = self.verify(_par, account2address)
            _token = self.load_base_account(self.address)
            _token.setParameters(_par)
            if _token is not None and my_account.address in _token.isLocked.keys()\
                    and _token.isLocked[my_account.address] == account2address and \
                    _token.isLocked[account2address] == my_account.address:
                self.isLocked[account2address] = my_account.address
                self.save()
                finish.finish = True
                return

        finish.finish = False

    def getAmount(self, token):
        return self.amount[token.address]

    def load_wallet(self):
        try:
            self.wallet = CWallet(self.address)
        except Exception as ex:
            print('load wallet', 'could not found wallet: '+str(ex))

    def save_atomic_transaction(self, atomic_transaction, announce=''):
        atomic_transaction.sender.load_wallet()
        _key = atomic_transaction.recipient.address
        _value = atomic_transaction.getParameters()
        _value.append(['Signature', atomic_transaction.sender.wallet.sign(str(_value))])

        self.kade.save(announce+_key, _value, announce=announce)

    def save_transaction(self, transaction, announce=''):
        _key = ';Transaction'
        _value = transaction.getParameters()
        self.kade.save(_key, _value, announce=announce)

    def send(self, recipient, token, amount, waiting_time=3600):
        from transaction import CAtomicTransaction
        self.load_wallet()
        time_to_close = dt.datetime.utcnow() + dt.timedelta(seconds=waiting_time)

        atomic = CAtomicTransaction(self, recipient, amount, optData='Simple TXN', token=token)
        recipient.save_atomic_transaction(atomic, announce='AtomicTransaction;')

        return atomic, time_to_close

    def send_loop(self, recipient, atomic, time_to_close, finish):
        recipient.save_atomic_transaction(atomic, announce='AtomicTransaction;')
        _signature = self.kade.look_at('SignatureRecipient;' + atomic.getHash())
        if _signature is not None:
            self.after_send_loop(recipient, atomic, _signature, time_to_close)
            finish.finish = True
            return

        finish.finish = False

    def after_send_loop(self, recipient, atomic, signature, time_to_close):
        from transaction import CTransaction
        self.load_wallet()
        _my_signature = self.wallet.sign(atomic.getHash())
        txn = CTransaction(time_to_close, 1)

        if self.chain.check_transaction_to_add(txn.check_add_return_hash(atomic, _my_signature, signature)):

            if txn.add(atomic, _my_signature, signature) < 2:
                raise Exception('Error in sending', 'Sending fails. Other fatal error')

            self.chain.addTransaction(txn)
            self.save_transaction(txn, announce='FinalTransaction;'+atomic.getHash())
            self.save()
            recipient.save()
        else:
            print('Transaction is just on place')

    def process_transaction(self, txn, time_to_close, atomicTransactions_list):
        time_to_close = dt.datetime.strptime(time_to_close, '%Y-%m-%dT%H:%M:%S')
        _txn = CTransaction(time_to_close, 1)
        _txn.setParameters(self.kade, txn)
        for i in range(_txn.noAtomicTransactions):
            _atomic = _txn.atomicTransactions[i]
            _atomic = CAtomicTransaction(atomicTransactions_list[i].sender, atomicTransactions_list[i].recipient,
                                         _atomic.amount, _atomic.optData, atomicTransactions_list[i].token, _atomic.time)
            _sender = _txn.senders[i]
            _recipient = _txn.recipients[i]
            _signSender = _txn.signatures[_sender.address]
            _signRecipient = _txn.signatures[_recipient.address]
            _txn.remove_atomic_for_addresses(_signSender, _signRecipient, _sender.address, _recipient.address)

            _hash = _txn.check_add_return_hash(_atomic, _signSender, _signRecipient)

            _txn.add(_atomic, _signSender, _signRecipient)
            _atomic.token.chain.addTransaction(_txn)
            _atomic.sender.chain.addTransaction(_txn)
            _atomic.recipient.chain.addTransaction(_txn)
            _atomic.token.save()
            _atomic.sender.save()
            _atomic.recipient.save()

    def getParameters(self):
        _uniqueAccounts, _accountsCreated, _transactions = self.chain.getParameters()
        return self.decimalPlace, self.amount, self.address, self.accountName, str(self.isLocked), self.main_account, \
               str({a: v for a, v in _accountsCreated.items()}), str(list(_uniqueAccounts.keys())), \
               str([v for v in _transactions.keys()])


    def setParameters(self, par, with_transactions=True):
        decimalPlace, amount, address, accountName, isLocked, main_account, acc_created, acc_chain, transactions = par

        acc_chain = str2obj(acc_chain)
        acc_created = str2obj(acc_created)
        transactions = str2obj(transactions)

        _temp_chain = {}
        for acc in acc_chain:
            _temp_chain[acc] = CBaseAccount(self.kade, '?', acc)
            _temp_chain[acc].update(deep=False)

        _temp_transactions = {}
        if with_transactions:

            for txn in transactions:
                _tx = CTransaction(dt.datetime.utcnow(), 1)
                par = self.kade.get('txn;' + txn)
                if par is not None:
                    _tx.setParameters(self.kade, par)
                    _temp_transactions[txn] = _tx
                else:
                    _temp_transactions[txn] = None
            self.chain.setParameters([acc_created, _temp_chain, _temp_transactions])

        self.decimalPlace = decimalPlace
        self.amount = amount
        self.address = address
        self.main_account = main_account
        self.isLocked = str2obj(isLocked)
        self.accountName = accountName

    def save_lock(self, key, value):
        print('SAVED = ' + str(self.kade.save(key, value, 'Lock;')))

    def save(self, announce='Account;', who_is_signing=None):
        _acc_chain, _acc_created, _transactions = self.chain.getParameters()

        self.save_transactions(_transactions)

        par = [self.decimalPlace, self.amount, self.address, trim_name(self.accountName), str(self.isLocked),
               self.main_account, str(_acc_created), str(list(_acc_chain.keys())), str(list(_transactions.keys()))]

        if self.accountName != '' and self.address != '' and self.accountName.find('?') < 0:

            if who_is_signing is None:
                self.load_wallet()
                who_is_signing = self

            try:
                par.append(['Signature', who_is_signing.wallet.sign(str(par))])
                self.verify(par, who_is_signing.address)

                print('SAVED = ' + str(self.kade.save(self.address, par, announce)))
            except:
                if self.wallet is None:
                    print('SAVED NO SIGN = ' + str(self.kade.save(self.address, self.address, announce='Invite;')))
                    print('No signature', 'wrong wallet was load')
                else:
                    messagebox.showwarning('Wallet error', 'Could not sign message with current wallet')

    def save_transactions(self, transactions):

        for _key, tx in transactions.items():
            if tx is not None:
                _value = tx.getParameters()
            else:
                _value = None
            self.kade.save(_key, _value, 'txn;')

    def update(self, deep=True):
        _par = self.kade.get('Account;' + self.address)

        if _par is not None:
            _par = self.verify(_par, self.address)
            if _par is not None:
                decimalPlace, amount, address, accountName, isLocked, main_account, _acc_created, _acc_chain, _txn = _par

                if deep:
                    self.setParameters([decimalPlace, amount, address, accountName, isLocked, main_account,
                                    _acc_created, _acc_chain, _txn])

        else:
            self.update_look_at()

    def update_look_at(self):
        _par = self.kade.look_at('Account;' + self.address)
        if _par is not None:
            _par = self.verify(_par, self.address)
            if _par is not None:
                decimalPlace, amount, address, accountName, isLocked, main_account, _acc_created, _acc_chain, _txn = _par
                self.setParameters([decimalPlace, amount, address, accountName, isLocked, main_account,
                                    _acc_created, _acc_chain, _txn])

    def verify(self, message, address):

        _signature = message[-1][1]
        _check = message[-1][0]
        _message = message[:-1]

        if not CWallet().verify(str(_message), _signature, address):
            raise Exception('Verification Fails', 'Message does not have valid signature' + str(message))

        return _message

    def show(self):
        ret = ' ' + self.accountName + ' = ' + str(self.address) + '\n'
        ret += ', '.join(['%s: %.2f' % (key[:5], value) for (key, value) in self.amount.items()])
        ret += '\nAccountsCreated: '
        ret += ', '.join(['%s: %d' % (key[:5], value) for (key, value) in self.chain.accountsCreated.items()])
        ret += '\nUniqueAccounts: '
        ret += ', '.join(['%s' % (key[:5]) for (key, value) in self.chain.uniqueAccounts.items()])
        ret += '\nLockedAccounts: '
        ret += ', '.join(['%s' % (key[:5]) for (key, value) in self.isLocked.items()])
        ret += '\nTransactions: '
        ret += ', '.join(['%s' % (key[:5]) for (key, value) in self.chain.transactions.items()])
        ret += '\nEnd print'
        print(ret)
        return ret
