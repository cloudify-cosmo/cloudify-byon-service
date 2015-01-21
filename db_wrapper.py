import leveldb
import json

class DBwrapper(object):

    def __init__(self):
        self.db = leveldb.LevelDB('./db')

    def add_default_auth(self, auth):
        self.default_auth = auth

    def add_server(self, server):
        if server.get('auth') is None:
            server['auth'] = self.default_auth
        self.db.Put(server['address'], str(server))

    def get_servers(self):
        servers = list()
        for (x, y) in self.db.RangeIter(include_value=True):
            json_server = json.loads(y.replace("'", "\""))
            servers.append(json_server)
        return servers

db = DBwrapper()