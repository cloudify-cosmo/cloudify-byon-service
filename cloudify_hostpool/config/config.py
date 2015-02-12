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

default = dict(auth=None, port=None)


def load_config(file_name):
    """ Main function loading config from YAML and returning
    generator of hosts dictionaries.

    :param file_name: name of file where pool configuration is provided

    :return host_generator: generator of host dictionaries
    """
    with open(file_name, 'r') as config_file:
        config = yaml.load(config_file)
    if config is None:
        raise ConfigError("Empty config")
    _set_default(config)
    if config.get('hosts'):
        return _add_hosts(config.get('hosts'))
    else:
        raise ConfigError("Unsupported key in configuration")


def _set_default(config):
    _default = config.get('default') \
        if config.get('default') is not None else {}
    global default
    if default is not None:
        default['auth'] = _default.get('auth')
        default['port'] = _default.get('port')


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
    """ Subnet hosts generator. Yields each host address given in ip range.
    """
    bin_sub = _ip2long(subnet)
    bin_broadcast = _get_broadcast_long(subnet, mask)
    for address in range(bin_sub + 1, bin_broadcast):
        yield _long2ip(address)


def _get_auth(host):
    if host.get('auth') is not None:
        auth = dict(host['auth'])
    elif default['auth']:
        auth = default['auth']
    else:
        raise ConfigError("No authorization given")
    return auth


def _get_port(host):
    if host.get('port') is not None:
        port = host['port']
    elif default['port']:
        port = default['port']
    else:
        raise ConfigError("No port given")
    return port


def _add_hosts(hosts):
    """ Create structured host generator (dictionary)
        host = {
            'public_ip': ip address or hostname (optional),
            'host': ip address or hostname,
            'port': port to communicate to,
            'auth': a dictionary with 'username' and 'keyfile' or 'password',
            'alive': flag that will inform if this host has been reachable
            recently,
            'reserved': flag informing if this host is to be assigned at the
            moment
        }
    """
    for host in hosts:
        if host.get('host') is not None:
            host['alive'] = False
            host['reserved'] = False
            host['auth'] = _get_auth(host)
            host['port'] = _get_port(host)
            yield host
        elif host.get('ip_range') is not None:
            subnet, mask = _get_subnet_and_mask(host.pop('ip_range'))
            hosts_list_gen = _get_subnet_hosts(subnet, mask)
            for host_ip in hosts_list_gen:
                auth = _get_auth(host)
                port = _get_port(host)
                _host = dict(host)
                s = dict(host=host_ip,
                         auth=auth,
                         alive=False,
                         reserved=False,
                         port=port)
                _host.update(s)
                yield _host
        else:
            raise ConfigError("Unsupported key in hosts configuration")
