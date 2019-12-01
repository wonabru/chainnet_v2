import datetime as dt
from Crypto import Hash
from wallet import CWallet, serialize
from isolated_functions import *
from atomicTransaction import CAtomicTransaction


class CTransaction:
    def __init__(self, timeToClose, noAtomicTransactions):
        self.atomicTransactions = []
        self.signatures = {}
        self.senders = []
        self.recipients = []
        self.timeToClose = str(dt.datetime.strftime(timeToClose, '%Y-%m-%d %H:%M:%S'))
        self.noAtomicTransactions = noAtomicTransactions

    def getParameters(self):
        _atomics = [atomic.getParameters() for atomic in self.atomicTransactions]
        _senders = [sender.getParameters() for sender in self.senders]
        _recipients = [recipient.getParameters() for recipient in self.recipients]
        _signatures = str(self.signatures)
        return [_atomics, _signatures, _senders, _recipients, self.timeToClose, self.noAtomicTransactions]

    def get_for_hash(self):
        _atomics = [atomic.get_for_hash() for atomic in self.atomicTransactions]
        _senders = [sender.address for sender in self.senders]
        _recipients = [recipient.address for recipient in self.recipients]
        _signatures = str(self.signatures)
        return _atomics, _signatures, _senders, _recipients, self.timeToClose, self.noAtomicTransactions

    def setParameters(self, DB, par):
        from account import CAccount

        _atomics, _signatures, _senders, _recipients, self.timeToClose, self.noAtomicTransactions = par

        response = {}
        try:
            response = str2obj(_signatures)
        except:
            pass
        self.signatures = response

        self.senders = []
        for _sender in _senders:
            _temp_sender = CAccount(DB, '?', None)
            _temp_sender.setParameters(_sender)
            _temp_sender.update()
            self.senders.append(_temp_sender)

        self.recipients = []
        for _recipient in _recipients:
            _temp_recipient = CAccount(DB, '?', None)
            _temp_recipient.setParameters(_recipient)
            _temp_recipient.update()
            self.recipients.append(_temp_recipient)


        self.atomicTransactions = []
        for _atomic in _atomics:
            _temp = CAtomicTransaction(CAccount(DB, '?', ""),
                                       CAccount(DB, '?', ""),
                                       -1, "",
                                       CAccount(DB, '?', ""))
            _temp.setParameters(_atomic)
            self.atomicTransactions.append(_temp)


    def check_add_return_hash(self, atomicTransaction, signSender, signRecipient):

        if self.noAtomicTransactions == len(self.atomicTransactions):
            raise Exception('Add Transaction',
                            'Stack is full. Please first remove one atomicTransaction in order to add new one')

        if self.verify(atomicTransaction, signSender, signRecipient) == False:
            raise Exception('Add Transaction', 'Verification fails')

        try:
            if dt.datetime.strptime(self.timeToClose, '%Y-%m-%d %H:%M:%S') < dt.datetime.strptime(
                    atomicTransaction.time, '%Y-%m-%d %H:%M:%S'):
                raise Exception('Add Transaction', 'Time to finish transaction just elapsed')

        except Exception as ex:
            raise Exception('Add Transaction', 'AtomicTransaction fails to build' + str(ex))

        self.atomicTransactions.append(atomicTransaction)
        self.senders.append(atomicTransaction.sender)
        self.recipients.append(atomicTransaction.recipient)

        self.signatures[atomicTransaction.sender.address] = signSender

        self.signatures[atomicTransaction.recipient.address] = signRecipient

        hash = self.getHash()

        self.atomicTransactions.remove(atomicTransaction)
        self.senders.remove(atomicTransaction.sender)
        self.recipients.remove(atomicTransaction.recipient)
        del self.signatures[atomicTransaction.sender.address]
        del self.signatures[atomicTransaction.recipient.address]

        return hash

    def add(self, atomicTransaction, signSender, signRecipient):
        
        self.check_add_return_hash(atomicTransaction, signSender, signRecipient)

        self.atomicTransactions.append(atomicTransaction)
        self.senders.append(atomicTransaction.sender)
        self.recipients.append(atomicTransaction.recipient)

        self.signatures[atomicTransaction.sender.address] = signSender

        self.signatures[atomicTransaction.recipient.address] = signRecipient

        if self.noAtomicTransactions == len(self.atomicTransactions):
            if self.checkTransaction():
                for atomic in self.atomicTransactions:
                    if atomic.sender.addAmount(atomic.token, -atomic.amount) == False or atomic.recipient.addAmount(atomic.token, atomic.amount) == False:
                        raise Exception('Add Transaction','sender has not enough funds')

                    atomic.sender.chain.addTransaction(self)
                    atomic.recipient.chain.addTransaction(self)
                    atomic.token.chain.addTransaction(self)

                    try:
                        del atomic.token.isLocked[atomic.sender.address]
                    except:
                        print('Add Transaction', "Key sender address not found in isLocked")
                    try:
                        del atomic.token.isLocked[atomic.recipient.address]
                    except:
                        print('Add Transaction', "Key recipient address not found in isLocked")

                    atomic.sender.save()
                    atomic.recipient.save()
                    atomic.token.save()

                    return 2
                return 1
            else:
                return 0
        return 1

    def remove(self, atomicTransaction, signSender, signRecipient):
        if self.verify(atomicTransaction, signSender, signRecipient) == False:
            raise Exception('Remove Transaction', 'Verification fails')

        self.atomicTransactions.remove(atomicTransaction)
        return True

    def remove_atomic_for_addresses(self, signSender, signRecipient, senderAddress, recipientAddress):

        _atomicTransactions = []
        for atomic in self.atomicTransactions:
            if atomic.sender.address != senderAddress and atomic.recipient.address != recipientAddress:
                _atomicTransactions.append(atomic)
            elif self.verify(atomic, signSender, signRecipient) == False:
                raise Exception('Remove Transaction', 'Verification fails')

        self.atomicTransactions = _atomicTransactions
        return True

    def checkTransaction(self):
        if self.noAtomicTransactions == 1:
            return True
        for atomic in self.atomicTransactions:
            if atomic.sender in self.recipients and atomic.recipient in self.senders \
                    and atomic.sender != atomic.recipient:
                continue
            raise Exception('Check Transaction', 'Not a full cycle')
        return True

    def getHash(self):
        digest = Hash.SHA256.new()
        digest.update(serialize(self.get_for_hash()))
        return digest.hexdigest()

    def verify(self, atomicTransaction, signSender, signRecipient):
        if CWallet().verify(atomicTransaction.getHash(), signSender, atomicTransaction.sender.address):
            if CWallet().verify(atomicTransaction.getHash(), signRecipient, atomicTransaction.recipient.address):
                return True
            else:
                raise Exception('Verify Transaction', 'Recipient signature is not valid')
        else:
            raise Exception('Verify Transaction', 'Sender signature is not valid')
