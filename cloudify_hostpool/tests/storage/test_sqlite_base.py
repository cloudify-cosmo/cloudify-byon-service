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

from cloudify_hostpool.storage import sqlite


class SQLiteTest(unittest.TestCase):
    db = None
    tempfile = None
    server_list = None

    @classmethod
    def setUpClass(cls):
        fd, cls.tempfile = tempfile.mkstemp()
        os.close(fd)
        cls.db = sqlite.SQLiteStorage(cls.tempfile)

    @classmethod
    def tearDownClass(cls):
        if cls.tempfile is not None:
            os.unlink(cls.tempfile)
            cls.tempfile = None

    def setUp(self):
        self.db = sqlite.SQLiteStorage(self.tempfile)

    def tearDown(self):
        with sqlite3.connect(self.tempfile) as conn:
            cursor = conn.cursor()
            cursor.execute('DROP TABLE {0}'
                           .format(sqlite.SQLiteStorage._TABLE_NAME))
            self.db = None