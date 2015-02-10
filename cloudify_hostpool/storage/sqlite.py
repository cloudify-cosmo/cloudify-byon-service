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


# will be moved to exceptions
class DBError(Exception):
    def __init__(self, message):
        super(DBError, self).__init__(message)


class DBLockedError(DBError):
    def __init__(self):
        super(DBLockedError, self).__init__("Database is locked")


class SQLiteStorage(AbstractStorage):
    """ Storage wrapper for SQLite DB implementing AbstractStorage interface"""
    _TABLE_NAME = 'servers'
    _CREATE_TABLE = 'CREATE TABLE IF NOT EXISTS {0} ' \
                    '(global_id integer PRIMARY KEY, server_id text, ' \
                    'private_ip text, public_ip text, auth text, ' \
                    'port text, alive integer, reserved integer)' \
        .format(_TABLE_NAME)

    def __init__(self, db_filename):
        self._filename = db_filename
        self._create_table()

    def get_servers(self, **filters):
        with sqlite3.connect(self._filename) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            if not filters:
                cursor.execute('SELECT * FROM {0}'
                               .format(SQLiteStorage._TABLE_NAME))
            else:
                sql_cond, values = self._get_sql_and_values_from_filters(
                    **filters)
                cursor.execute('SELECT * FROM {0} WHERE {1}'
                               .format(SQLiteStorage._TABLE_NAME, sql_cond),
                               values)
            result = cursor.fetchall()
            return list(result)

    def add_server(self, server):
        with sqlite3.connect(self._filename) as conn:
            cursor = conn.cursor()
            values = (server.get('server_id'), server['private_ip'],
                      server['public_ip'], json.dumps(server['auth']),
                      server['port'], server['alive'], server['reserved'])
            cursor.execute('INSERT INTO {0} (server_id, private_ip, '
                           'public_ip, auth, port, alive, reserved)'
                           ' VALUES(?, ?, ?, ?, ?, ?, ?)'
                           .format(SQLiteStorage._TABLE_NAME), values)
            server['global_id'] = cursor.lastrowid

    def update_server(self, global_id, server):
        if not server:
            return None
        try:
            with sqlite3.connect(self._filename, isolation_level='EXCLUSIVE')\
                    as conn:
                conn.row_factory = self._dict_factory
                conn.execute('BEGIN EXCLUSIVE')
                cursor = conn.cursor()
                values = tuple(server.itervalues())
                sql_part = ", ".join('{0}=?'.format(s) for s in server)
                cursor.execute('SELECT * FROM {0} WHERE global_id=?'
                               .format(SQLiteStorage._TABLE_NAME),
                               (global_id, ))
                srv = cursor.fetchone()
                if all(item in srv.iteritems() for item in server.iteritems()):
                    return None
                cursor.execute('UPDATE {0} SET {1} WHERE global_id=?'
                               .format(SQLiteStorage._TABLE_NAME, sql_part),
                               values + (global_id,))
                srv.update(server)
                return srv
        except sqlite3.OperationalError as e:
            if e.message == 'database is locked':
                raise DBLockedError()
            raise DBError(e.message)

    def get_server(self, **filters):
        if not filters:
            return None
        with sqlite3.connect(self._filename) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            sql_part, values = self._get_sql_and_values_from_filters(**filters)
            cursor.execute('SELECT * FROM {0} WHERE {1}'
                           .format(SQLiteStorage._TABLE_NAME, sql_part),
                           values)
            return cursor.fetchone()

    def reserve_server(self, global_id):
        while True:
            try:
                with sqlite3.connect(self._filename) as conn:
                    conn.row_factory = self._dict_factory
                    conn.isolation_level = 'EXCLUSIVE'
                    conn.execute('BEGIN EXCLUSIVE')
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM {0} WHERE global_id=?'
                                   .format(self._TABLE_NAME), (global_id,))
                    result = cursor.fetchone()
                    if result['reserved']:
                        return False
                    cursor.execute('UPDATE {0} SET reserved=1 '
                                   'WHERE global_id=?'
                                   .format(self._TABLE_NAME), (global_id,))
                    return True
            except sqlite3.OperationalError as e:
                if e.message != 'database is locked':
                    raise DBError(e.message)

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

    def _get_sql_and_values_from_filters(self, **filters):
        """ Helper method to create sql query """
        values = tuple(filters.itervalues())
        sql_part = ' AND '.join('{0}=?'.format(f) for f in filters)
        return sql_part, values
