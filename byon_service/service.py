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
from flask import Flask
from flask import jsonify
from flask_restful import Api
import byon_service.exceptions
import httplib

app = Flask(__name__)
api = Api(app)


@app.errorhandler(byon_service.exceptions.ByonHTTPException)
def handle_byon_errors(error):
    response = jsonify(error.to_dict())
    response.status_code = error.get_code()
    return response


@app.route('/servers', methods=['GET'])
def list_servers():
    """ List allocated servers"""
    server = {'function': 'list_servers'}
    return jsonify(server), httplib.NOT_FOUND


@app.route('/servers', methods=['POST'])
def acquire_servers():
    """ Acquire(allocate) the server """
    server = {'function': 'acquire_server'}
    # do the magic
    # use method raising NoResourcesException if there is no such
    # server assigned
    return jsonify(server), httplib.CREATED


@app.route('/servers/<server_id>', methods=['DELETE'])
def release_server(server_id):
    """Release the server with the given server_id"""
    server = {'function': 'release_server', 'server': server_id}
    # use method raising NotFoundError if there is no such server assigned
    return jsonify(server), httplib.OK


@app.route('/servers/<server_id>', methods=['GET'])
def get_server(server_id):
    """Get the details of the server with the given server_id"""
    server = {'function': 'get_server', 'server': server_id}
     # use method raising NotFoundError if there is no such server assigned
    raise byon_service.exceptions.NotFoundError(server_id)
    return jsonify(server), httplib.OK

if __name__ == '__main__':
    app.run()
