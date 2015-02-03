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

default_auth = None


def load_config(storage, file_name):
    """ Main function loading config from yaml file to the storage.
    Storage is an object of a class implementing AbstractStorage"""
    with open(file_name, 'r') as config_file:
        config = yaml.load(config_file)
    default = config.get('default')
    global default_auth
    if default is not None:
        default_auth = default.get('auth')
    _add_servers(storage, config.get('hosts'))


def _ip2long(ip):
    # throws socket.error if IP is not valid
    return struct.unpack('!L', socket.inet_aton(ip))[0]


def _long2ip(num):
    return socket.inet_ntoa(struct.pack('!L', num))


def _get_ibitmask(mask):
    return (2L << (31-int(mask))) - 1


def _get_broadcast_long(subnet, mask):
    s = _ip2long(subnet)
    m = _get_ibitmask(int(mask))
    return s | m


def _get_subnet_and_mask(ip_range):
    # throws socket.error if IP is not valid
    regex = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}")
    result = regex.findall(ip_range)
    if len(result) != 1:
        raise socket.error("illegal IP address string")
    s, m = ip_range.split('/')
    return s, m


def _get_subnet_hosts(subnet, mask):
    """ Subnet hosts generator.
    Yields each server address given in ip range.
    """
    bin_sub = _ip2long(subnet)
    bin_imask = _get_ibitmask(mask)
    bin_broadcast = bin_sub | bin_imask
    for address in range(bin_sub, bin_broadcast):
        yield _long2ip(address)


def _add_servers(storage, servers):
    """ Add server to database creating the server structure (dictionary)
        server = {
            'address': ip address or hostname,
            'port': port to communicate to,
            'auth': a dictionary with 'username' and 'keyfile' or 'password',
            'alive': flag that will inform if this server has been reachable
            recently,
            'reserved': flag informing if this server is to be assigned at the
            moment
        }
    """
    for server in servers:
        if server.get('address') is not None:
            server['alive'] = False
            server['reserved'] = False
            if server.get('auth') is None:
                server['auth'] = dict(default_auth)
            server['port'] = server['auth'].pop('port')
            storage.add_server(server)
        elif server.get('ip_range') is not None:
            subnet, mask = _get_subnet_and_mask(server.get('ip_range'))
            servers_list_gen = _get_subnet_hosts(subnet, mask)
            for server_ip in servers_list_gen:
                auth = dict(default_auth)
                if server.get('auth') is not None:
                    auth = dict(server['auth'])
                s = {'address': server_ip,
                     'auth': auth,
                     'alive': False,
                     'reserved': False}
                s['port'] = s['auth'].pop('port')
                storage.add_server(s)
        else:
            return False  # wrong config

