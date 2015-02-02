# #######
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
import json
import sqlite3
from storage_interface import AbstractStorage


class SQLiteStorage(AbstractStorage):
    """ Storage wrapper for SQLite DB implementing AbstractStorage interface"""
    _CREATE_TABLE = 'CREATE TABLE IF NOT EXISTS servers ' \
                    '(server_global_id integer PRIMARY KEY, server_id text, ' \
                    'address text, auth text, port integer, alive integer, ' \
                    'reserved integer)'

    def __init__(self, db_filename):
        self._filename = db_filename
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self._filename) as conn:
            cursor = conn.cursor()
            cursor.execute(SQLiteStorage._CREATE_TABLE)

    def _dict_factory(self, cursor, row):
        """ Create dictionary out of fetched row by db cursor"""
        d = {}
        for idx, col in enumerate(cursor.description):
            if col[0] == 'auth':
                # "auth" column value is dictionary serialized to string
                # -> json.dumps(auth).
                d[col[0]] = json.loads(row[idx])
            else:
                d[col[0]] = row[idx]
        return d

    def _get_sql_and_values_from_kwargs(self, **kwargs):
        """ Helper method to create sql query """
        values = tuple(kwargs.itervalues())
        sql_part = ' AND '.join('{0}=?'.format(k) for k in kwargs)
        return sql_part, values

    def get_servers(self, **kwargs):
        with sqlite3.connect(self._filename) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            if not kwargs:
                cursor.execute('SELECT * FROM servers')
            else:
                sql_cond, values = self._get_sql_and_values_from_kwargs(
                    **kwargs)
                cursor.execute('SELECT * FROM servers WHERE ' + sql_cond,
                               values)
            result = cursor.fetchall()
            return list(result)

    def add_server(self, server):
        with sqlite3.connect(self._filename) as conn:
            cursor = conn.cursor()
            values = (server.get('server_id'), server['address'],
                      json.dumps(server['auth']), server['port'],
                      server['alive'], server['reserved'])
            cursor.execute('INSERT INTO servers '
                           '(server_id, address, auth, port, alive, reserved) '
                           'VALUES(?, ?, ?, ?, ?, ?)', values)
            server['server_global_id'] = cursor.lastrowid
            return server

    def update_server(self, server, **kwargs):
        with sqlite3.connect(self._filename) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            values = tuple(kwargs.itervalues())
            sql_part = ", ".join('{0}=?'.format(k) for k in kwargs)
            cursor.execute('UPDATE servers SET ' + sql_part +
                           'WHERE server_global_id=?',
                           values + (server['server_global_id'],))
            if cursor.rowcount == 0:
                return False, None
            conn.commit()
            cursor.execute('SELECT * FROM servers WHERE server_global_id=?',
                           (server['server_global_id'],))
            return True, cursor.fetchone()

    def get_server(self, **kwargs):
        if not kwargs:
            return None
        with sqlite3.connect(self._filename) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            sql_part, values = self._get_sql_and_values_from_kwargs(**kwargs)
            cursor.execute('SELECT * FROM servers WHERE ' + sql_part, values)
            return cursor.fetchone()

    def reserve_server(self, server):
        with sqlite3.connect(self._filename) as conn:
            conn.row_factory = self._dict_factory
            conn.isolation_level = 'EXCLUSIVE'
            conn.execute('BEGIN EXCLUSIVE')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM servers WHERE server_global_id=?',
                           (server['server_global_id'],))
            result = cursor.fetchone()
            if result['reserved']:
                return False
            cursor.execute('UPDATE servers SET reserved=1 '
                           'WHERE server_global_id=?',
                           (server['server_global_id'],))
            return True

db = SQLiteStorage('test.db')
