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
from cloudify_hostpool.tests.storage import test_sqlite_base


class SQLiteTest(test_sqlite_base.SQLiteTest):

    def test_get_all_empty(self):
        result = self.db.get_hosts()
        self.assertEqual(result, [])

    def test_add_host(self):
        host = {
            'host': '127.0.0.1',
            'public_address': '127.0.0.1',
            'port': 22,
            'auth': None,
            'host_id': None,
            'alive': False,
            'reserved': False
        }
        self.db.add_host(host)
        result = self.db.get_hosts()
        self.assertEqual(len(result), 1)
        db_host = result[0]
        self.assertEqual(db_host, host)

    def test_add_bad_host(self):
        host = {
            'port': 22,
            'auth': None,
            'host_id': None,
            'alive': False,
            'reserved': False
        }
        self.assertRaises(KeyError, self.db.add_host, host)

    def test_get_filtered_hosts(self):
        self._add_hosts()

        result = self.db.get_hosts()
        self.assertEqual(len(result), len(self.host_list))

        result = self.db.get_hosts(port=1000)
        self.assertEqual(len(result), 2)

        result = self.db.get_hosts(alive=True)
        self.assertEqual(len(result), 2)

        result = self.db.get_hosts(alive=True, port=1000)
        self.assertEqual(len(result), 1)

    def test_update_host(self):
        self.assertIsNone(self.db.update_host('whatever', None))

        self._add_hosts()
        result = self.db.get_hosts()
        host = result[0]
        host_update = {
            'reserved': True
        }
        updated_host = self.db.update_host(host['global_id'], host_update)
        self.assertEqual(updated_host['global_id'], host['global_id'])
        self.assertNotEqual(updated_host['reserved'], host['reserved'])
        self.assertEqual(updated_host['reserved'], host_update['reserved'])
        updated_host2 = self.db.update_host(host['global_id'], host_update)
        self.assertIsNone(updated_host2)

    def test_get_host_global_id(self):
        self._add_hosts()
        hosts = self.db.get_hosts()
        db_host = hosts[0]
        host = self.db.get_host(global_id=db_host['global_id'])
        self.assertEqual(db_host, host)
        host = self.db.get_host(global_id=10)
        self.assertIsNone(host)

    def test_get_host_filter(self):
        self._add_hosts()
        hosts = self.db.get_hosts()
        db_host = hosts[0]
        # it should return first alive host
        host = self.db.get_host(alive=True)
        self.assertEqual(db_host, host)

    def test_reserve_host(self):
        self._add_hosts()
        hosts = self.db.get_hosts()
        db_host = hosts[0]

        result = self.db.reserve_host(db_host['global_id'])
        self.assertTrue(result)

        result = self.db.reserve_host(db_host['global_id'])
        self.assertFalse(result)

        host = self.db.get_host(global_id=db_host['global_id'])
        self.assertEqual(db_host['host'], host['host'])
        self.assertEqual(db_host['port'], host['port'])
        self.assertEqual(db_host['auth'], host['auth'])
        self.assertEqual(db_host['host_id'], host['host_id'])
        self.assertEqual(db_host['alive'], host['alive'])
        self.assertNotEqual(db_host['reserved'], host['reserved'])
        self.assertTrue(host['reserved'])
        self.assertEqual(db_host['global_id'], host['global_id'])

    def _add_hosts(self):
        self.host_list = [
            {
                'host': '127.0.0.1',
                'public_address': '127.0.0.1',
                'port': 22,
                'auth': None,
                'host_id': None,
                'alive': True,
                'reserved': False
            },
            {
                'host': '127.0.0.1',
                'public_address': '127.0.0.1',
                'port': 1000,
                'auth': None,
                'host_id': None,
                'alive': False,
                'reserved': False
            },
            {
                'host': '10.0.0.1',
                'public_address': '10.0.0.1',
                'port': 1000,
                'auth': None,
                'host_id': None,
                'alive': True,
                'reserved': False
            }
        ]
        for host in self.host_list:
            self.db.add_host(host)
