#!byonvenv/bin/python
from flask import Flask
import sqlite3
import yaml

app = Flask(__name__)

def get_db_cursor():
    conn = sqlite3.connect('test_sqlite')
    conn.row_factory = dict_factory
    return conn.cursor(), conn

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        if col[0] in ('username', 'keyfile', 'port', 'password'):
            if d.get('auth') is None:
                d['auth'] = {}
            d['auth'][col[0]] = row[idx]
        else:
            d[col[0]] = row[idx]
    return d

@app.route('/servers/list', methods=['GET'])
def list_hosts():
    c, conn = get_db_cursor()
    c.execute("SELECT address, S.status, A.username, A.keyfile, A.password FROM node as N JOIN status as S on N.status=S.id JOIN auth as A on A.id = N.auth")
    results = c.fetchall()
    conn.close()
    return yaml.safe_dump(results)

@app.route('/servers/list/<status>', methods=['GET'])
def list_filtered_hosts(status):
    c, conn = get_db_cursor()
    c.execute("SELECT address, S.status, A.username, A.keyfile, A.password FROM node as N JOIN status as S on N.status=S.id JOIN auth as A on A.id = N.auth WHERE S.status=?", (status,))
    results = c.fetchall()
    conn.close()
    return yaml.safe_dump(results)

@app.route('/servers/take/<number>', methods=['POST'])
def take_servers(number):
    #do the magic
    return str(number) +  yaml.dump(hosts)

@app.route('/servers/release', methods=['POST'])
def release_servers():
    #do the other magic
    return "Release"

if __name__ == '__main__':
    app.run(debug=True)
