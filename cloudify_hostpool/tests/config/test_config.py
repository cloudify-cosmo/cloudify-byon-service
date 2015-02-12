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
import StringIO
import socket
import unittest

from mock import MagicMock
from mock import patch

from cloudify_hostpool.config import config


class ConfigurationTest(unittest.TestCase):
    def test_get_broadcast(self):
        ip = '123.213.123.232'
        mask = '30'
        self.assertEqual('123.213.123.235',
                         config._long2ip(config._get_broadcast_long(ip, mask)))

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

    def test_add_hosts_host(self):
        hosts = [
            dict(host='2.2.2.1', port=22,
                 auth={'username': 'ubuntu', 'pass': 'pass2'}),
            dict(host='2.2.2.2', port=22,
                 auth={'username': 'ubuntu2', 'pass': 'pass2'})
        ]
        saved_hosts = list(config._add_hosts(hosts))
        self.assertEqual(len(saved_hosts), len(hosts))

    def test_add_hosts_ip_range(self):
        hosts = [
            dict(ip_range='2.2.2.8/29',
                 auth={'username': 'ubuntu3', 'pass': 'pass2'}, port=22)
        ]
        saved_hosts = list(config._add_hosts(hosts))
        self.assertEqual(len(saved_hosts), 6)

    def test_add_hosts_error(self):
        hosts = [
            dict(auth={'username': 'ubuntu3', 'pass': 'pass2'}, port=22)
        ]
        self.assertRaises(config.ConfigError,
                          lambda: list(config._add_hosts(hosts)))
        hosts = [
            dict(ip='2.2.2.8',
                 auth={'username': 'ubuntu3', 'pass': 'pass2'}, port=22)
        ]
        self.assertRaises(config.ConfigError,
                          lambda: list(config._add_hosts(hosts)))
        hosts = [
            dict(host='2.2.2.8',

                 auth={'username': 'ubuntu3', 'pass': 'pass2'})
        ]
        self.assertRaises(config.ConfigError,
                          lambda: list(config._add_hosts(hosts)))
        hosts = [
            dict(ip_range='2.2.2.8/29')
        ]
        config.default_auth = dict(username='adam', password='eve')
        self.assertRaises(config.ConfigError,
                          lambda: list(config._add_hosts(hosts)))
        config.default_auth = None

    def test_load_config(self):
        _file = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'resources/pool.yaml')
        loaded_hosts = list(config.load_config(_file))
        self.assertEqual(len(loaded_hosts), 4)

    def test_bad_config(self):
        _file = StringIO.StringIO("bad_key: \nbad_key: test")
        m = MagicMock(return_value=_file)
        _file.__enter__ = MagicMock(return_value=_file)
        _file.__exit__ = MagicMock()
        with patch('__builtin__.open', m):
            self.assertRaises(config.ConfigError, config.load_config, _file)

    def test_empty_config(self):
        _file = StringIO.StringIO("")
        m = MagicMock(return_value=_file)
        _file.__enter__ = MagicMock(return_value=_file)
        _file.__exit__ = MagicMock()
        with patch('__builtin__.open', m):
            self.assertRaises(config.ConfigError, config.load_config, 'x')
