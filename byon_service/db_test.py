import os
path = os.path.abspath('..')
import sys
print path
sys.path.append(path)
from storage_sqlite import db
from config import load_config


load_config('byon.yaml')
print db.get_servers()
s1 = db.get_server(address='192.168.101.17', server_global_id=4)
print s1
print db.update_server(s1, address='192.168.1.17')
print db.get_server(server_global_id=4)

