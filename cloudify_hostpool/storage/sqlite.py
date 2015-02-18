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
from cloudify_hostpool.exceptions import DBError
from cloudify_hostpool.exceptions import DBLockedError


class _SQLiteStorageBase(AbstractStorage):
    """ Storage wrapper for SQLite DB implementing AbstractStorage interface"""
    _TABLE_NAME = 'hosts'
    _CREATE_TABLE = 'CREATE TABLE IF NOT EXISTS {0} ' \
                    '(global_id integer PRIMARY KEY, host_id text, ' \
                    'host text, public_address text, auth text, ' \
                    'port text, alive integer, reserved integer)' \
        .format(_TABLE_NAME)

    def __init__(self, db_filename, blocking):
        self.blocking = blocking
        self._filename = db_filename
        self._create_table()

    def get_hosts(self, **filters):
        with sqlite3.connect(self._filename) as conn:
            conn.row_factory = _dict_factory
            cursor = conn.cursor()
            if not filters:
                cursor.execute('SELECT * FROM {0}'
                               .format(_SQLiteStorageBase._TABLE_NAME))
            else:
                sql_cond, values = _get_sql_and_values_from_filters(
                    **filters)
                cursor.execute('SELECT * FROM {0} WHERE {1}'
                               .format(_SQLiteStorageBase._TABLE_NAME,
                                       sql_cond),
                               values)
            return list(cursor.fetchall())

    def add_host(self, host):
        with sqlite3.connect(self._filename) as conn:
            cursor = conn.cursor()
            values = (host.get('host_id'), host['host'],
                      host.get('public_address'), json.dumps(host['auth']),
                      host['port'], host['alive'], host['reserved'])
            cursor.execute('INSERT INTO {0} (host_id, host, '
                           'public_address, auth, port, alive, reserved)'
                           ' VALUES(?, ?, ?, ?, ?, ?, ?)'
                           .format(_SQLiteStorageBase._TABLE_NAME), values)
            host['global_id'] = cursor.lastrowid

    def update_host(self, global_id, host):
        if not host:
            return None
        while True:
            try:
                with sqlite3.connect(self._filename,
                                     isolation_level='EXCLUSIVE') as conn:
                    conn.row_factory = _dict_factory
                    conn.execute('BEGIN EXCLUSIVE')
                    cursor = conn.cursor()
                    values = tuple(host.itervalues())
                    sql_part = ", ".join('{0}=?'.format(s) for s in host)
                    cursor.execute('SELECT * FROM {0} WHERE global_id=?'
                                   .format(_SQLiteStorageBase._TABLE_NAME),
                                   (global_id, ))
                    hst = cursor.fetchone()
                    if all(item in hst.iteritems()
                           for item in host.iteritems()):
                        return None
                    cursor.execute('UPDATE {0} SET {1} WHERE global_id=?'
                                   .format(_SQLiteStorageBase._TABLE_NAME,
                                           sql_part),
                                   values + (global_id,))
                    hst.update(host)
                    return hst
            except sqlite3.OperationalError as e:
                if e.message == 'database is locked':
                    if self.blocking:
                        continue
                    else:
                        raise DBLockedError()
                raise DBError(e.message)

    def get_host(self, **filters):
        if not filters:
            return None
        with sqlite3.connect(self._filename) as conn:
            conn.row_factory = _dict_factory
            cursor = conn.cursor()
            sql_part, values = _get_sql_and_values_from_filters(**filters)
            cursor.execute('SELECT * FROM {0} WHERE {1}'
                           .format(_SQLiteStorageBase._TABLE_NAME, sql_part),
                           values)
            return cursor.fetchone()

    def reserve_host(self, global_id):
        while True:
            try:
                with sqlite3.connect(self._filename) as conn:
                    conn.row_factory = _dict_factory
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
            cursor.execute(_SQLiteStorageBase._CREATE_TABLE)


class SQLiteStorageBlocking(_SQLiteStorageBase):
    '''Blocking version of the SQLite storage wrapper'''

    def __init__(self, db_filename):
        super(SQLiteStorageBlocking, self).__init__(db_filename, True)


class SQLiteStorageNonblocking(_SQLiteStorageBase):
    '''Nonblocking version of the SQLite storage wrapper'''

    def __init__(self, db_filename):
        super(SQLiteStorageNonblocking, self).__init__(db_filename, False)


_CUSTOM_PARSERS = {
    # `auth` column's value is a dictionary serialized to a JSON string.
    'auth': json.loads
}


def _dict_factory(cursor, row):
    """ Create dictionary out of fetched row by db cursor"""
    result = {}
    for idx, col in enumerate(cursor.description):
        name = col[0]
        content = row[idx]
        if name in _CUSTOM_PARSERS:
            result[name] = _CUSTOM_PARSERS[name](content)
        else:
            result[name] = content
    return result


def _get_sql_and_values_from_filters(**filters):
    """ Helper method to create sql query """
    values = tuple(filters.itervalues())
    sql_part = ' AND '.join('{0}=?'.format(f) for f in filters)
    return sql_part, values
