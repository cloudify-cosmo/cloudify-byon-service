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
import threading
from Queue import Queue

from cloudify_hostpool.storage import sqlite
from cloudify_hostpool.tests.storage import test_sqlite_base


class SQLiteTestThreading(test_sqlite_base.SQLiteTest):

    def test_reserving(self):
        """
        Test spawning 1000 threads and checking if more than 0 has raised
        DBLockError, check if this host was changed only one time.
        """
        self._add_host()
        host = self.db.get_host(host='127.0.0.1')
        results = Queue()
        thr = []
        exceptions = Queue()
        thread_number = 100
        for x in xrange(thread_number):
            t = threading.Thread(
                target=self._reserve, args=(host['global_id'], results,
                                            exceptions))
            t.start()
            thr.append(t)
        for t in thr:
            t.join()
        rows_changed = 0
        rows_not_changed = 0
        while not results.empty():
            if results.get() is True:
                rows_changed += 1
            else:
                rows_not_changed += 1
        self.assertEqual(exceptions.qsize(), 0)
        self.assertEqual(rows_changed, 1)
        self.assertEqual(rows_not_changed,
                         thread_number - rows_changed - exceptions.qsize())

    def test_updating(self):
        """
        Test spawning 1000 threads and checking if more than 0 has raised
        DBLockError, check if this host was changed only one time.
        """
        self._add_host()
        host = self.db.get_host(host='127.0.0.1')
        update = dict(public_address='127.0.5.1', port=23, alive=False)
        results = Queue()
        thr = []
        exceptions = Queue()
        thread_number = 1000
        for x in xrange(thread_number):
            t = threading.Thread(
                target=self._update, args=(host['global_id'], update,
                                           results, exceptions))
            t.start()
            thr.append(t)
        for t in thr:
            t.join()
        rows_changed = 0
        rows_not_changed = 0
        while not results.empty():
            if results.get() is not None:
                rows_changed += 1
            else:
                rows_not_changed += 1
        self.assertGreater(exceptions.qsize(), 0)
        self.assertEqual(rows_changed, 1)
        self.assertEqual(rows_not_changed,
                         thread_number - rows_changed - exceptions.qsize())

    def _reserve(self, g_id, results, exceptions):
        try:
            results.put(self.db.reserve_host(g_id))
        except sqlite.DBError:
            exceptions.put(True)

    def _update(self, g_id, update, results, exceptions):
        try:
            results.put(self.db.update_host(g_id, update))
        except sqlite.DBLockedError:
            exceptions.put(True)

    def _add_host(self):
        host = dict(host='127.0.0.1', public_address='127.0.0.1', port=22,
                    auth=None, host_id=None, alive=True, reserved=False)
        self.db.add_host(host)
