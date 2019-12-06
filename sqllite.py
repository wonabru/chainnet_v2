from sqlitedict import SqliteDict, SqliteMultithread
import os

class CDataBase(object):
    def __init__(self):
        try:
            self.close()
        except:
            pass
        self.mydict = SqliteDict(os.path.join('DB', 'my_db.sqlite'), autocommit=True)
        self.show('')

    def set(self, key, value):
        self.mydict[key] = value

    def iskey(self, key):
        return key in self.mydict.keys()

    def get(self, key):
        ret = None
        try:
            ret = self.mydict[key]
        except KeyError:

            for k in self.mydict.keys():
                if key == k[:len(key)]:
                    ret = self.mydict[k]
                    break
        return ret
    
    def show(self, start_with=''):
        for key, value in self.mydict.items():
            if key.find(start_with) >= 0:
                print(key, '\t', value, '\n')
    
    def clear(self, key):
        if key in self.mydict.keys():
            del self.mydict[key]
        
    def close(self):
        self.mydict.close()
