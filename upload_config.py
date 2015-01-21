import yaml
import struct
import socket
from db_wrapper import db


def load_config(file_name):
    config_file = open(file_name, 'r')
    config = yaml.load(config_file)
    default = config.get('default')
    if default is not None:
        default_auth = default.get('auth')
        if default_auth is not None:
            db.add_default_auth(default_auth)
    add_servers(config.get('hosts'))


def show_hosts():
    return db.get_servers()


def ip2long(ip):
    return struct.unpack('!L', socket.inet_aton(ip))[0]


def long2ip(num):
    return socket.inet_ntoa(struct.pack('!L',num))


def get_ibitmask(mask):
    return (2L << (31-int(mask))) - 1


def get_broadcast_long(subnet, mask):
    s = ip2long(subnet)
    m = get_ibitmask(int(mask))
    return s | m


def get_subnet_and_mask(ip_range):
    s, m = ip_range.split('/')
    return s, m


def add_subnet_hosts(subnet, mask):
    servers_list = []
    bin_sub = ip2long(subnet)
    bin_imask = get_ibitmask(mask)
    bin_broadcast = bin_sub | bin_imask

    for address in range(bin_sub, bin_broadcast):
        servers_list.append(long2ip(address))
    return servers_list


def add_servers(servers):
    for server in servers:
        if server.get('address') is not None:
            db.add_server(server)
        if server.get('ip_range') is not None:
            subnet, mask = get_subnet_and_mask(server.get('ip_range'))
            servers_list = add_subnet_hosts(subnet, mask)
            for server_ip in servers_list:
                if server.get('auth') is None:
                    server['auth'] = db.default_auth
                s = {"address": server_ip, 'auth': server['auth']}
                db.add_server(s)

