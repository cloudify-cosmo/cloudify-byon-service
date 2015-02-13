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
import os
import sqlite3
import tempfile
import unittest

from cloudify_hostpool.exceptions import DBLockedError


class ConcurrentSQLiteTest(unittest.TestCase):
    db = None
    tempfile = None
    _TABLE_NAME = 'test'

    def setUp(self):
        fd, self.tempfile = tempfile.mkstemp()
        os.close(fd)
        connection = sqlite3.connect(self.tempfile)
        connection.execute('CREATE TABLE {0} (id integer primary key)'
                           .format(self._TABLE_NAME))
        connection.close()

    def tearDown(self):
        if self.tempfile is not None:
            os.unlink(self.tempfile)
            self.tempfile = None

    def test_check_exclusive_transaction(self):
        self.assertRaises(DBLockedError, self._check_exclusive_transaction)

    def _check_exclusive_transaction(self):
        try:
            connection1 = sqlite3.connect(self.tempfile)
            connection1.execute('BEGIN EXCLUSIVE')
            cursor1 = connection1.cursor()
            cursor1.execute('SELECT * FROM {0}'.format(self._TABLE_NAME))

            connection2 = sqlite3.connect(self.tempfile)
            cursor2 = connection2.cursor()
            cursor2.execute('SELECT * FROM {0}'.format(self._TABLE_NAME))

            connection1.close()
            connection2.close()
        except sqlite3.OperationalError as e:
            if e.message == 'database is locked':
                raise DBLockedError()
            raise e
