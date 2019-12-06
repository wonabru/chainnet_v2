from sqllite import CDataBase as sqllite
from kademliaGetSet import CDataBase
import socket
from isolated_functions import *
import time
import multiprocessing as mp

instance_kade = None

class CSQLLite():
    def __init__(self):

        global instance_kade
        if instance_kade is None:
            node_identifier = socket.gethostbyname(socket.gethostname())
            self.sqllite = sqllite()
            self.nodes = ["3.113.39.120", "192.168.0.38", "192.168.56.1", "10.0.2.2", "10.0.2.15", "127.0.0.1", node_identifier]
            self.kade = CDataBase()
            self.kade.initiate()
            instance_kade = self
        else:
            self.nodes = instance_kade.nodes
            self.sqllite = instance_kade.sqllite
            self.kade = instance_kade.kade

    def save(self, key, value, announce=''):
        if not isinstance(key, str):
            key = str(key)
        key = announce + key
        _current = self.sqllite.get('KADEMLIA')
        if _current is None:
            self.sqllite.set(key='KADEMLIA', value=[key, ])
        else:
            _current.append(key)
            _current = list(set(_current))
            self.sqllite.set(key='KADEMLIA', value=_current)

        self.announce(key, str(value))

        self.sqllite.set(key, str(value))

        return self.sqllite.get(key)

    def clone_kademlia(self):

        key_list = self.sqllite.get('KADEMLIA')
        if key_list is not None:
            for key in key_list:
                value = self.look_at(key)
                if value is not None:
                    self.sqllite.set(key=key, value=str(value))
                else:
                    print('NO key found in KADEMLIA: {}'.format(key))

    def get(self, key):
        return self.look_at(key)

    def clear(self, key, announce=''):
        if not isinstance(key, str):
            key = str(key)
        key = announce + key
        _current = self.sqllite.get('KADEMLIA')
        if _current is not None and key in _current:

            _current.remove(key)
            self.sqllite.set(key='KADEMLIA', value=_current)

        self.kade.clear(key)

        self.sqllite.clear(key)

    def announce(self, key, value):
        self.kade.set(key=key, value=str(value))

    def look_at(self, key):
        if not isinstance(key, str):
            key = str(key)
        response = self.sqllite.get(key)
        if response is None:
            response = self.kade.get(key=key)

        if response is not None:
            try:
                response = str2obj(response)
            except:
                pass
        return response

    def close(self):
        self.sqllite.close()

    def register_node(self, address):
        if address not in self.nodes:
            self.nodes.append(address)

    def bootstrapNodes(self):
        self.kade.bootstrap(self.nodes)
