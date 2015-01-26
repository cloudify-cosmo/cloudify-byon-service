import sqlitedict
import uuid

class DBwrapper(object):

    def __init__(self):
        self.db = sqlitedict.SqliteDict('/tmp/sqlitedict', flag='n', autocommit='True')

    def add_default_auth(self, auth):
        self.default_auth = auth

    def get_servers(self):
        return list(self.db.itervalues())

    def add_server(self, server):
        server['server_global_identifier'] = uuid.uuid1()
        self.db[server['address']] = server

db = DBwrapper()
