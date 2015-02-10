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
        result = self.db.get_servers()
        self.assertEqual(result, [])

    def test_add_server(self):
        server = {
            'private_ip': '127.0.0.1',
            'public_ip': '127.0.0.1',
            'port': '22',
            'auth': None,
            'server_id': None,
            'alive': False,
            'reserved': False
        }
        self.db.add_server(server)
        result = self.db.get_servers()
        self.assertEqual(len(result), 1)
        db_server = result[0]
        self.assertEqual(db_server, server)

    def test_add_bad_server(self):
        server = {
            'port': '22',
            'auth': None,
            'server_id': None,
            'alive': False,
            'reserved': False
        }
        self.assertRaises(KeyError, self.db.add_server, server)

    def test_get_filtered_servers(self):
        self._add_servers()

        result = self.db.get_servers()
        self.assertEqual(len(result), len(self.server_list))

        result = self.db.get_servers(port='1000')
        self.assertEqual(len(result), 2)

        result = self.db.get_servers(alive=True)
        self.assertEqual(len(result), 2)

        result = self.db.get_servers(alive=True, port='1000')
        self.assertEqual(len(result), 1)

    def test_update_server(self):
        self.assertIsNone(self.db.update_server('whatever', None))

        self._add_servers()
        result = self.db.get_servers()
        server = result[0]
        server_update = {
            'reserved': True
        }
        updated_server = self.db.update_server(server['global_id'],
                                               server_update)
        self.assertEqual(updated_server['global_id'], server['global_id'])
        self.assertNotEqual(updated_server['reserved'], server['reserved'])
        self.assertEqual(updated_server['reserved'],
                         server_update['reserved'])
        updated_server2 = self.db.update_server(server['global_id'],
                                                server_update)
        self.assertIsNone(updated_server2)

    def test_get_server_global_id(self):
        self._add_servers()
        servers = self.db.get_servers()
        db_server = servers[0]
        server = self.db.get_server(global_id=db_server['global_id'])
        self.assertEqual(db_server, server)

    def test_get_server_filter(self):
        self._add_servers()
        servers = self.db.get_servers()
        db_server = servers[0]
        # it should return first alive server
        server = self.db.get_server(alive=True)
        self.assertEqual(db_server, server)

    def test_reserve_server(self):
        self._add_servers()
        servers = self.db.get_servers()
        db_server = servers[0]

        result = self.db.reserve_server(db_server['global_id'])
        self.assertTrue(result)

        result = self.db.reserve_server(db_server['global_id'])
        self.assertFalse(result)

        server = self.db.get_server(global_id=db_server['global_id'])
        self.assertEqual(db_server['private_ip'], server['private_ip'])
        self.assertEqual(db_server['port'], server['port'])
        self.assertEqual(db_server['auth'], server['auth'])
        self.assertEqual(db_server['server_id'], server['server_id'])
        self.assertEqual(db_server['alive'], server['alive'])
        self.assertNotEqual(db_server['reserved'], server['reserved'])
        self.assertTrue(server['reserved'])
        self.assertEqual(db_server['global_id'], server['global_id'])

    def _add_servers(self):
        self.server_list = [
            {
                'private_ip': '127.0.0.1',
                'public_ip': '127.0.0.1',
                'port': '22',
                'auth': None,
                'server_id': None,
                'alive': True,
                'reserved': False
            },
            {
                'private_ip': '127.0.0.1',
                'public_ip': '127.0.0.1',
                'port': '1000',
                'auth': None,
                'server_id': None,
                'alive': False,
                'reserved': False
            },
            {
                'private_ip': '10.0.0.1',
                'public_ip': '10.0.0.1',
                'port': '1000',
                'auth': None,
                'server_id': None,
                'alive': True,
                'reserved': False
            }
        ]
        for server in self.server_list:
            self.db.add_server(server)
