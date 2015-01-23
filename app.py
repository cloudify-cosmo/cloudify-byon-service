#!byonvenv/bin/python
from flask import Flask
from flask import jsonify
from db_wrapper import db

app = Flask(__name__)

@app.route('/servers', methods=['GET'])
def list_hosts():
    return jsonify(servers=db.get_servers())

@app.route('/servers', methods=['POST'])
def aquire_server():
    #do the magic
    return ""

@app.route('/servers/', methods=['POST'])
def release_server():
    #do the other magic
    return "Release"

if __name__ == '__main__':
    app.run(debug=True)
