import leveldb
import json
import uuid

class DBwrapper(object):

    def __init__(self, db_file):
        self.db = leveldb.LevelDB(db_file)

    def add_default_auth(self, auth):
        self.default_auth = auth

    def add_server(self, server):
        if server.get('auth') is None:
            server['auth'] = self.default_auth
        server['server_global_identifier'] = str(uuid.uuid1())
        self.db.Put(server['address'], str(server))

    def get_servers(self):
        servers = list()
        for (_, serialized_server) in self.db.RangeIter(include_value=True):
            json_server = json.loads(serialized_server.replace("'", "\""))
            servers.append(json_server)
        return servers

db = DBwrapper('./db')