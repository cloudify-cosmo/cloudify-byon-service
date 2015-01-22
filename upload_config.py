import yaml
import sqlite3
import struct
import socket




# add port
def add_auth(auth):
    if auth is None:
        return None
    conn = open_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO auth (username, password, keyfile) VALUES (?,?,?)',
              (auth.get('username'),
               auth.get('password'),
               auth.get('keyfile')))
    auth_id = c.lastrowid
    conn.commit()
    conn.close()
    return auth_id

def show_auths():
    conn = open_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM auth')
    res = c.fetchall()
    conn.close()
    return res

def show_hosts():
    conn = open_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM node')
    res = c.fetchall()
    conn.close()
    return res

def add_hosts(hosts, default_auth_id):
    conn = sqlite3.connect('test_sqlite')
    c = conn.cursor()
    for h in hosts:
        if h.get('address') is not None:
            address = h.get('address')
            if h.get('auth') is not None:
                auth = add_auth(h.get('auth'))
            else:
                auth = default_auth_id
            c.execute('SELECT id from status where status=\"inactive\"')
            status, = c.fetchone()
            c.execute('INSERT INTO node (address, auth, status) VALUES (?,?,?)', (address, auth, status))
        if h.get('ip_range') is not None:
            subnet, mask = get_subnet_and_mask(h.get('ip_range'))
            h_list = add_subnet_hosts(subnet, mask, conn)
    conn.commit()
    conn.close()

def ip2long(ip):
    return struct.unpack('!L', socket.inet_aton(ip))[0]

def long2ip(num):
    return socket.inet_ntoa(struct.pack('!L',num))

def get_ibitmask(mask):
    return (2L << (31-mask)) - 1

def get_broadcast_long(subnet, mask):
    s = ip2long(subnet)
    m = get_ibitmask(int(mask))
    return s | m

def get_subnet_and_mask(ip_range):
    s, m = ip_range.split('/')
    return s, m

def add_subnet_hosts(subnet, mask, conn):


config_file = open("byon.yaml", 'r')
config = yaml.load(config_file)
print "Config: "
print config
print config.get('default')
default_auth_id = add_auth(config['default']['auth'])
add_hosts(config['hosts'], default_auth_id)
print "All auths: " + str(show_auths())
print "All hosts: " + str(show_hosts())

