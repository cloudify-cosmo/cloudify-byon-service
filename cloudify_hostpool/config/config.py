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
import re
import socket
import struct

import yaml

from cloudify_hostpool.exceptions import ConfigError

default_auth = None


def load_config(file_name):
    """ Main function loading config from YAML and returning
    generator of server dictionaries.

    :param file_name: name of file where pool configuration is provided

    :return server_generator: generator of server dictionaries
    """
    with open(file_name, 'r') as config_file:
        config = yaml.load(config_file)
    if config is None:
        raise ConfigError("Empty config")
    _set_default_auth(config)
    if config.get('hosts'):
        return _add_servers(config.get('hosts'))
    else:
        raise ConfigError("Unsupported key in configuration")


def _set_default_auth(config):
    default = config.get('default')
    global default_auth
    if default is not None:
        default_auth = default.get('auth')


def _ip2long(ip):
    # throws socket.error if IP is not valid
    return struct.unpack('!L', socket.inet_aton(ip))[0]


def _long2ip(num):
    return socket.inet_ntoa(struct.pack('!L', num))


def _get_ibitmask(mask):
    return (2L << (32 - int(mask)) - 1) - 1


def _get_broadcast_long(subnet, mask):
    bin_sub = _ip2long(subnet)
    bin_imask = _get_ibitmask(int(mask))
    return bin_sub | bin_imask


def _get_subnet_and_mask(ip_range):
    # throws socket.error if IP is not valid
    regex = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}")
    result = regex.findall(ip_range)
    if len(result) != 1:
        raise socket.error("illegal IP address string")
    s, m = ip_range.split('/')
    return s, m


def _get_subnet_hosts(subnet, mask):
    """ Subnet hosts generator. Yields each server address given in ip range.
    """
    bin_sub = _ip2long(subnet)
    bin_broadcast = _get_broadcast_long(subnet, mask)
    for address in range(bin_sub + 1, bin_broadcast):
        yield _long2ip(address)


def _validate_config_auth(auth):
    mandatory_keys = ['username', 'port']
    if not all(key in auth.iterkeys() for key in mandatory_keys):
        raise ConfigError("Error in authorization")


def _get_auth(server):
    if server.get('auth') is not None:
        auth = dict(server['auth'])
    elif default_auth:
        auth = dict(default_auth)
    else:
        raise ConfigError("No authorization given")
    _validate_config_auth(auth)
    return auth


def _add_servers(servers):
    """ Add server to database creating the server structure (dictionary)
        server = {
            'public_ip': ip address or hostname,
            'private_ip': ip address or hostname,
            'port': port to communicate to,
            'auth': a dictionary with 'username' and 'keyfile' or 'password',
            'alive': flag that will inform if this server has been reachable
            recently,
            'reserved': flag informing if this server is to be assigned at the
            moment
        }
    """
    for server in servers:
        if server.get('private_ip') is not None:
            server['alive'] = False
            server['reserved'] = False
            server['auth'] = _get_auth(server)
            server['port'] = server['auth'].pop('port')
            yield server
        elif server.get('ip_range') is not None:
            subnet, mask = _get_subnet_and_mask(server.pop('ip_range'))
            servers_list_gen = _get_subnet_hosts(subnet, mask)
            for server_ip in servers_list_gen:
                auth = _get_auth(server)
                _server = dict(server)
                s = dict(private_ip=server_ip,
                         auth=auth,
                         alive=False,
                         reserved=False,
                         port=auth.pop('port'))
                _server.update(s)
                yield _server
        else:
            raise ConfigError("Unsupported key in hosts configuration")
