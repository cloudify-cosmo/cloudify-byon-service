import sqlite3
import json

class DBwrapper(object):

    def __init__(self):
        self.conn = None
        self.cursor = None
        self.TABLE_NAME = 'servers'
        self._open_db()
        self._create_table()
        self._close_db()

    def _create_table(self):
        sql = 'CREATE TABLE IF NOT EXISTS %s ' \
              '(server_global_id INTEGER PRIMARY KEY, data TEXT)' \
              % self.TABLE_NAME
        self._execute_and_commit(sql)

    def _open_db(self):
        self.conn = sqlite3.connect('sqlite')
        self.cursor = self.conn.cursor()

    def _close_db(self):
        self.conn.close()

    def _execute(self, statement):
        self.cursor.execute(statement)

    def _execute_and_commit(self, statement):
        self.cursor.execute(statement)
        self.conn.commit()

    def add_default_auth(self, auth):
        self.default_auth = auth

    def get_servers(self):
        self._open_db()
        sql = 'SELECT * FROM %s' % self.TABLE_NAME
        self._execute(sql)
        raw_servers = self.cursor.fetchall()
        self._close_db()
        servers = []
        for (server_uid, serialized_server) in raw_servers:
            json_server = json.loads(serialized_server.replace("'", "\""))
            json_server['server_global_identifier'] = server_uid
            servers.append(json_server)
        return servers

    def add_server(self, server):
        self._open_db()
        sql = 'INSERT INTO %s (data) VALUES (\"%s\")'\
              % (self.TABLE_NAME, str(server))
        self._execute_and_commit(sql)
        self._close_db()

db = DBwrapper()
