########
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
import httplib

from flask import Flask
from flask import jsonify
from flask_restful import Api

from cloudify_hostpool import exceptions
from cloudify_hostpool.rest.backend import rest_backend

app = Flask(__name__)
api = Api(app)
backend = rest_backend.RestBackend('test.yaml', 'test.db')


@app.errorhandler(exceptions.HostPoolHTTPException)
def handle_byon_errors(error):
    response = jsonify(error.to_dict())
    response.status_code = error.get_code()
    return response


@app.route('/hosts', methods=['GET'])
def list_hosts():
    """ List allocated hosts"""
    hosts = backend.list_hosts()
    return jsonify(hosts=hosts), httplib.OK


@app.route('/hosts', methods=['POST'])
def acquire_host():
    """ Acquire(allocate) the host """
    host = backend.acquire_host()
    return jsonify(host), httplib.CREATED


@app.route('/hosts/<host_id>', methods=['DELETE'])
def release_host(host_id):
    """Release the host with the given host_id"""
    host = backend.release_host(host_id)
    return jsonify(host), httplib.OK


@app.route('/hosts/<host_id>', methods=['GET'])
def get_host(host_id):
    """Get the details of the host with the given host_id"""
    host = backend.get_host(host_id)
    return jsonify(host), httplib.OK

if __name__ == '__main__':
    app.run()
