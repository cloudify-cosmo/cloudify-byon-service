#!byonvenv/bin/python
from flask import Flask
from flask import jsonify
from upload_config import load_config
from db_wrapper import db

app = Flask(__name__)
load_config('byon.yaml')

@app.route('/servers', methods=['GET'])
def list_hosts():
    results = db.get_servers()
    return jsonify(servers=results)

@app.route('/servers/aquire', methods=['POST'])
def take_servers(number):
    #do the magic
    return str(number)

@app.route('/servers/release', methods=['DELETE'])
def release_servers():
    #do the other magic
    return "Release"

if __name__ == '__main__':
    app.run(debug=True)
