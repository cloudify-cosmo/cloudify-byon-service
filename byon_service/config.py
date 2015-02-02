import yaml
import struct
import socket
from storage_sqlite import db

default_auth = None


def load_config(file_name):
    with open(file_name, 'r') as config_file:
        config = yaml.load(config_file)
    default = config.get('default')
    global default_auth
    if default is not None:
        default_auth = default.get('auth')
    add_servers(config.get('hosts'))


def ip2long(ip):
    return struct.unpack('!L', socket.inet_aton(ip))[0]


def long2ip(num):
    return socket.inet_ntoa(struct.pack('!L', num))


def get_ibitmask(mask):
    return (2L << (31-int(mask))) - 1


def get_broadcast_long(subnet, mask):
    s = ip2long(subnet)
    m = get_ibitmask(int(mask))
    return s | m


def get_subnet_and_mask(ip_range):
    s, m = ip_range.split('/')
    return s, m


#TODO: optimize, possible solutions: insert to db in a loop
def add_subnet_hosts(subnet, mask):
    servers_list = []
    bin_sub = ip2long(subnet)
    bin_imask = get_ibitmask(mask)
    bin_broadcast = bin_sub | bin_imask
    for address in range(bin_sub, bin_broadcast):
        servers_list.append(long2ip(address))
    return servers_list


def add_servers(servers):
    global default_auth
    for server in servers:
        if server.get('address') is not None:
            server['alive'] = False
            server['reserved'] = False
            if server.get('auth') is None:
                server['auth'] = dict(default_auth)
            server['port'] = server['auth'].pop('port')
            print server
            db.add_server(server)
        elif server.get('ip_range') is not None:
            subnet, mask = get_subnet_and_mask(server.get('ip_range'))
            servers_list = add_subnet_hosts(subnet, mask)
            for server_ip in servers_list:
                auth = dict(default_auth)
                if server.get('auth') is not None:
                    auth = dict(server['auth'])
                s = {'address': server_ip,
                     'auth': auth,
                     'alive': False,
                     'reserved': False}
                s['port'] = s['auth'].pop('port')
                db.add_server(s)
        #TODO: add else -> if sth else config is wrong
