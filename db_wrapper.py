import leveldb

class DBwrapper(object):

    def __init__(self):
        self.db = leveldb.LevelDB('./db')
        self.incrementator = 1

    def add_host(self, host):
        self.db.Put(self.incrementator, host)
        self.incrementator += 1

    def get_hosts(self):
        hosts = []
        for h in self.db.RangeIter(include_value=True):
            hosts.append(h)
        return hosts