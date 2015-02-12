########
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

from mock import patch

from cloudify_hostpool.exceptions import NotFoundError
from cloudify_hostpool.rest.backend.rest_backend import RestBackend
from cloudify_hostpool.storage import sqlite


class RestBackendTest(unittest.TestCase):
    db = None
    tempfile = None
    host_list = None

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

    @patch('cloudify_hostpool.config.config.load_config')
    def test_list_hosts(self, mock_config):
        mock_config.return_value = []
        self._add_hosts()
        self.rest_backend = RestBackend(self.tempfile, 'test')
        self.rest_backend.storage = self.db
        self.assertEqual(len(self.rest_backend.list_hosts()), 1)

    @patch('cloudify_hostpool.config.config.load_config')
    def test_release_host(self, mock_config):
        mock_config.return_value = []
        self._add_hosts()
        self.rest_backend = RestBackend(self.tempfile, 'test')
        self.rest_backend.storage = self.db
        host_id = 'test'
        self.db.update_host(1, dict(host_id=host_id))
        host = self.rest_backend.release_host(host_id)
        self.assertIsNone(host['host_id'])

    @patch('cloudify_hostpool.config.config.load_config')
    def test_release_host_error(self, mock_config):
        mock_config.return_value = []
        self._add_hosts()
        self.rest_backend = RestBackend(self.tempfile, 'test')
        self.rest_backend.storage = self.db
        host_id = 'test'
        self.assertRaises(NotFoundError,
                          self.rest_backend.release_host, host_id)

    @patch('cloudify_hostpool.config.config.load_config')
    def test_get_host(self, mock_config):
        mock_config.return_value = []
        self._add_hosts()
        self.rest_backend = RestBackend(self.tempfile, 'test')
        self.rest_backend.storage = self.db
        host_id = 'test'
        self.db.update_host(1, dict(host_id=host_id))
        host = self.rest_backend.get_host(host_id)
        reference = self.db.get_host(global_id=1)
        self.assertEqual(host, reference)

    @patch('cloudify_hostpool.config.config.load_config')
    def test_get_host_error(self, mock_config):
        mock_config.return_value = []
        self._add_hosts()
        self.rest_backend = RestBackend(self.tempfile, 'test')
        self.rest_backend.storage = self.db
        host_id = 'test'
        self.assertRaises(NotFoundError,
                          self.rest_backend.get_host, host_id)

    def _add_hosts(self):
        self.host_list = [
            {
                'host': '127.0.0.1',
                'public_address': '127.0.0.1',
                'port': '22',
                'auth': None,
                'host_id': None,
                'alive': True,
                'reserved': False
            },
            {
                'host': '127.0.0.1',
                'public_address': '127.0.0.1',
                'port': '1000',
                'auth': None,
                'host_id': None,
                'alive': False,
                'reserved': False
            },
            {
                'host': '10.0.0.1',
                'public_address': '10.0.0.1',
                'port': '1000',
                'auth': None,
                'host_id': None,
                'alive': True,
                'reserved': False
            },
            {
                'host': '10.0.0.4',
                'public_address': '10.0.0.4',
                'port': '1000',
                'auth': None,
                'host_id': '',
                'alive': True,
                'reserved': False
            }
        ]
        for host in self.host_list:
            self.db.add_host(host)
