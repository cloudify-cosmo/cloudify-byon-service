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
import os
import unittest
import tempfile

import yaml
from mock import MagicMock
from mock import patch

from cloudify_hostpool.rest.backend import rest_backend

_CONFIG = {'default': {'auth': {'username': 'x'}, 'port': 123},
           'hosts': [{'host': 'google.com', 'port': 80}]}


class ServiceTest(unittest.TestCase):
    def setUp(self):
        fd, self.config = tempfile.mkstemp()
        os.close(fd)
        with open(self.config, 'w') as f:
            f.write(yaml.dump(_CONFIG))
        fd, self.db = tempfile.mkstemp()
        os.close(fd)
        backend = rest_backend.RestBackend(self.config, self.db)

        self.p = patch('cloudify_hostpool.rest.service._init_backend',
                       MagicMock(return_value=None))
        self.p.start()
        from cloudify_hostpool.rest import service
        service.backend = backend
        self.app = service.app.test_client()

    def tearDown(self):
        self.p.stop()
        if self.config is not None:
            os.unlink(self.config)
            self.config = None
        if self.db is not None:
            os.unlink(self.db)
            self.db = None

    def test_list_hosts(self):
        result = self.app.get('/hosts')
        self.assertEqual(result._status_code, 200)

    def test_acquire(self):
        result = self.app.post('/hosts')
        self.assertEqual(result._status_code, 201)

    def test_acquire_and_not_ok(self):
        self.app.post('/hosts')
        result = self.app.post('/hosts')
        self.assertEqual(result._status_code, 515)

    def test_get_not_ok(self):
        result = self.app.get('/hosts/test')
        self.assertEqual(result._status_code, 404)

    def test_acquire_and_release(self):
        result = self.app.post('/hosts')
        self.assertEqual(result._status_code, 201)
        host = json.loads(result.response.next())
        result = self.app.post('/hosts')
        self.assertEqual(result._status_code, 515)
        result = self.app.delete('/hosts/{0}'.format(host['host_id']))
        self.assertEqual(result._status_code, 200)
        result = self.app.post('/hosts')
        self.assertEqual(result._status_code, 201)
