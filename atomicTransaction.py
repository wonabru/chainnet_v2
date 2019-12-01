from Crypto import Hash
import datetime as dt
from wallet import serialize


def check_if_common_connection(sender, recipient):
    list1 = list(sender.chain.uniqueAccounts.keys()) + [sender.address]
    list2 = list(recipient.chain.uniqueAccounts.keys()) + [recipient.address]

    if not any(e in list2 for e in list1):
        raise Exception('Atomic transaction', 'sender and recipient have no common connections')

    return True


def check_if_my_connection(token, creator):
    list1 = list(token.chain.uniqueAccounts.keys()) + [token.address]

    if creator.address in list1:
        return True
    else:
        raise Exception('Atomic transaction', 'token and creator are not connected')


class CAtomicTransaction:
    def __init__(self, sender, recipient, amount, optData, token, time=None):

        self.token = token
        self.sender = sender
        self.recipient = recipient
        self.amount = 0
        self.optData = ""
        self.time = ""
        if amount < 0:
            return

        if sender.address == recipient.address:
            raise Exception('Atomic transaction', 'sender cannot be the same as recipient')

        if sender.address not in token.isLocked.keys():
            raise Exception('Atomic transaction', 'Cannot perform transaction. Lock sender account first')

        if recipient.address not in token.isLocked.keys():
            raise Exception('Atomic transaction', 'Cannot perform transaction. Lock recipient account first')

        if token.isLocked[sender.address] != recipient.address:
            raise Exception('Atomic transaction', 'Sender account is locked, but not for the recipient')

        if token.isLocked[recipient.address] != sender.address:
            raise Exception('Atomic transaction', 'Recipient account is locked, but not for the sender')

        check_if_common_connection(sender, recipient)

        if recipient.address not in token.chain.uniqueAccounts:
            token.chain.uniqueAccounts[recipient.address] = recipient
        self.token = token
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.optData = optData
        if time is None:
            self.time = str(dt.datetime.strftime(dt.datetime.today(), '%Y-%m-%d %H:%M:%S'))
        else:
            self.time = time

    def getParameters(self):
        _token = self.token.getParameters()
        _sender = self.sender.getParameters()
        _recipient = self.recipient.getParameters()
        return [_token, _sender, _recipient, self.amount, self.optData, self.time]

    def setParameters(self, par):
        _token, _sender, _recipient, self.amount, self.optData, self.time = par
        self.token.setParameters(_token)
        self.token.update()
        self.sender.setParameters(_sender)
        self.sender.update()
        self.recipient.setParameters(_recipient)
        self.recipient.update()

    def get_for_hash(self):
        _token = self.token.address
        _sender = self.sender.address
        _recipient = self.recipient.address
        return _token + _sender + _recipient + str(self.amount) + str(self.optData) + self.time

    def getHash(self):
        digest = Hash.SHA256.new()
        digest.update(serialize(self.get_for_hash()))
        return digest.hexdigest()
