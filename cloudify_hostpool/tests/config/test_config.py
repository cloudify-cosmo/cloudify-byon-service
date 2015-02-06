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
import socket
import unittest

from cloudify_hostpool.config import config


class DummyStorage(object):

    def __init__(self):
        self.db = []

    def add_server(self, server):
        self.db.append(server)

    def get_servers(self):
        return self.db


class ConfigurationTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ConfigurationTest, self).__init__(*args, **kwargs)
        self.storage = None

    def setUp(self):
        self.storage = DummyStorage()

    def tearDown(self):
        self.storage = None

    def test_get_broadcast(self):
        ip = '123.213.123.232/30'
        self.assertEqual(('123.213.123.232', '30'),
                         config._get_subnet_and_mask(ip))

    def test_get_subnet_and_mask(self):
        ip = '123.213.123.232/30'
        self.assertEqual(('123.213.123.232', '30'),
                         config._get_subnet_and_mask(ip))

    def test_get_subnet_and_mask_wrong_ip(self):
        ip = '123.213.123.232dasfsdf'
        self.assertRaises(socket.error, config._get_subnet_and_mask, ip)
        ip = '123.213..232/30'
        self.assertRaises(socket.error, config._get_subnet_and_mask, ip)
        ip = 'dasfsdf'
        self.assertRaises(socket.error, config._get_subnet_and_mask, ip)

    def test_get_subnet_hosts(self):
        subnet = '2.2.2.0'
        mask = '29'
        ips = list(config._get_subnet_hosts(subnet, mask))
        self.assertEqual(len(ips), 6)

        subnet = '2.2.2.8'
        mask = '29'
        ips = list(config._get_subnet_hosts(subnet, mask))
        self.assertEqual(len(ips), 6)

        subnet = '2.2.2.16'
        mask = '29'
        ips = list(config._get_subnet_hosts(subnet, mask))
        self.assertEqual(len(ips), 6)

        subnet = '2.2.2.248'
        mask = '29'
        ips = list(config._get_subnet_hosts(subnet, mask))
        self.assertEqual(len(ips), 6)

    def test_add_servers_private_ip(self):
        hosts = [
            dict(private_ip='2.2.2.1',
                 auth={'username': 'ubuntu', 'pass': 'pass2', 'port': 22}),
            dict(private_ip='2.2.2.2',
                 auth={'username': 'ubuntu2', 'pass': 'pass2', 'port': 22})
        ]
        print "Before: ", self.storage.get_servers()
        config._add_servers(self.storage, hosts)
        saved_servers = self.storage.get_servers()
        print self.storage.get_servers()
        self.assertEqual(len(saved_servers), len(hosts))

    def test_add_servers_ip_range(self):
        hosts = [
            dict(ip_range='2.2.2.8/29',
                 auth={'username': 'ubuntu3', 'pass': 'pass2', 'port': 22})
        ]
        config._add_servers(self.storage, hosts)
        saved_servers = self.storage.get_servers()
        self.assertEqual(len(saved_servers), 6)

    def test_add_servers_error(self):
        hosts = [
            dict(auth={'username': 'ubuntu3', 'pass': 'pass2', 'port': 22})
        ]
        self.assertRaises(config.ConfigError, config._add_servers,
                          self.storage, hosts)
        hosts = [
            dict(ip='2.2.2.8',
                 auth={'username': 'ubuntu3', 'pass': 'pass2', 'port': 22})
        ]
        self.assertRaises(config.ConfigError, config._add_servers,
                          self.storage, hosts)
        hosts = [
            dict(private_ip='2.2.2.8',
                 auth={'username': 'ubuntu3', 'pass': 'pass2'})
        ]
        self.assertRaises(config.ConfigError, config._add_servers,
                          self.storage, hosts)
        hosts = [
            dict(ip_range='2.2.2.8/29')
        ]
        config.default_auth = dict(username='adam', password='eve')
        self.assertRaises(config.ConfigError, config._add_servers,
                          self.storage, hosts)
        config.default_auth = None

    def test_load_config(self):
        _file = 'cloudify_hostpool/tests/config/pool.yaml'
        config.load_config(self.storage, _file)
        self.assertEqual(len(self.storage.get_servers()), 4)
