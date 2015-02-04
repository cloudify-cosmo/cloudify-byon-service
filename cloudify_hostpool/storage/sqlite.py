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

from cloudify_hostpool.storage.base import AbstractStorage


class SQLiteStorage(AbstractStorage):
    """ Storage wrapper for SQLite DB implementing AbstractStorage interface"""
    _CREATE_TABLE = 'CREATE TABLE IF NOT EXISTS servers ' \
                    '(global_id integer PRIMARY KEY, server_id text, ' \
                    'address text, auth text, port integer, alive integer, ' \
                    'reserved integer)'

    def __init__(self, db_filename):
        self._filename = db_filename
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self._filename) as conn:
            cursor = conn.cursor()
            cursor.execute(SQLiteStorage._CREATE_TABLE)

    def get_servers(self, **filters):
        with sqlite3.connect(self._filename) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            if not filters:
                cursor.execute('SELECT * FROM servers')
            else:
                sql_cond, values = self._get_sql_and_values_from_filters(
                    **filters)
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
                           '(server_id, address, auth, port, alive, reserved)'
                           ' VALUES(?, ?, ?, ?, ?, ?)', values)
            server['global_id'] = cursor.lastrowid

    def update_server(self, global_id, server):
        if not server:
            return None
        with sqlite3.connect(self._filename) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            values = tuple(server.itervalues())
            sql_part = ", ".join('{0}=?'.format(s) for s in server)
            cursor.execute('UPDATE servers SET {0} WHERE global_id=?'
                           .format(sql_part),
                           values + (global_id,))
            if cursor.rowcount == 0:
                return None
            conn.commit()
            cursor.execute('SELECT * FROM servers WHERE global_id=?',
                           (global_id,))
            return cursor.fetchone()

    def get_server(self, **filters):
        if not filters:
            return None
        with sqlite3.connect(self._filename) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            sql_part, values = self._get_sql_and_values_from_filters(**filters)
            cursor.execute('SELECT * FROM servers WHERE ' + sql_part, values)
            return cursor.fetchone()

    def reserve_server(self, server):
        with sqlite3.connect(self._filename) as conn:
            conn.row_factory = self._dict_factory
            conn.isolation_level = 'EXCLUSIVE'
            conn.execute('BEGIN EXCLUSIVE')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM servers WHERE global_id=?',
                           (server['global_id'],))
            result = cursor.fetchone()
            if result['reserved']:
                return False
            cursor.execute('UPDATE servers SET reserved=1 WHERE global_id=?',
                           (server['global_id'],))
            return True

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

    def _get_sql_and_values_from_filters(self, **filters):
        """ Helper method to create sql query """
        values = tuple(filters.itervalues())
        sql_part = ' AND '.join('{0}=?'.format(f) for f in filters)
        return sql_part, values
