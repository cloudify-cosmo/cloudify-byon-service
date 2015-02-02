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
    def __init__(self, db_filename):
        self.filename = db_filename
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.filename) as conn:
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE IF NOT EXISTS servers '
                           '(server_global_id integer PRIMARY KEY, '
                           'server_id text, address text, auth text, '
                           'port integer, alive integer, reserved integer)')

    def _dict_factory(self, cursor, row):
        d = dict()
        for idx, col in enumerate(cursor.description):
            if col[0] == 'auth':
                auth = row[idx].replace("'", "\"")
                d[col[0]] = json.loads(auth)
            else:
                d[col[0]] = row[idx]
        return d

    def _get_sql_and_values_from_kwargs(self, **kwargs):
        values = tuple(kwargs.itervalues())
        sql_part = ""
        for column in kwargs.iterkeys():
            sql_part += '{0}=? AND '.format(column)
        sql_part = sql_part[:-4]  # remove last "AND "
        return sql_part, values

    def get_servers(self, **kwargs):
        with sqlite3.connect(self.filename) as conn:
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
        try:
            with sqlite3.connect(self.filename) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO servers(server_id, address, auth, '
                               'port, alive, reserved) '
                               'VALUES(?, ?, ?, ?, ?, ?)',
                               (server.get('server_id'),
                                server['address'],
                                str(server['auth']),
                                server['port'],
                                server['alive'],
                                server['reserved']))
                server['server_global_id'] = cursor.lastrowid
                return server
        except sqlite3.IntegrityError:
            print 'Could not add server twice'

    def update_server(self, server, **kwargs):
        with sqlite3.connect(self.filename) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            values = tuple(kwargs.itervalues())
            sql_part = ""
            for column in kwargs.iterkeys():
                sql_part += '{0}=?, '.format(column)
            sql_part = sql_part[:-2]  # remove last ", "
            cursor.execute('UPDATE servers SET ' + sql_part +
                           'WHERE server_global_id=?',
                           values + (server['server_global_id'],))
            if cursor.rowcount == 0:
                return False
            conn.commit()
            cursor.execute('SELECT * FROM servers WHERE server_global_id=?',
                           (server['server_global_id'],))
            return cursor.fetchone()

    def get_server(self, **kwargs):
        if not kwargs:
                return None
        with sqlite3.connect(self.filename) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            sql_part, values = self._get_sql_and_values_from_kwargs(**kwargs)
            cursor.execute('SELECT * FROM servers WHERE ' + sql_part, values)
            return cursor.fetchone()

    def reserve_server(self, server):
        with sqlite3.connect(self.filename) as conn:
            conn.row_factory = self._dict_factory
            conn.isolation_level = 'EXCLUSIVE'
            conn.execute('BEGIN EXCLUSIVE')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM servers WHERE server_global_id=?',
                           (server['server_global_id'],))
            result = cursor.fetchone()
            if result['reserved']:
                return False
            cursor.execute('UPDATE servers SET reserved=1')
            return True

db = SQLiteStorage('test.db')
