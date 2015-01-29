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


class NoResourcesError(Exception):
    """Raised when there is no servers left to be acquired"""

    def __init__(self):
        self.status_code = 515
        self.text = "Cannot acquire server. " \
                    "The pool is empty or all servers are in use."
        super(NoResourcesError, self).__init__(self.text)

    def get_code(self):
        return self.status_code

    def to_dict(self):
        return {'message': self.text}

    def __str__(self):
        return repr(self.text)


class NotFoundError(Exception):
    """Raised when there is no server with requested id"""

    def __init__(self, server_id):
        self.status_code = 404
        self.text = "Cannot find requested server. "
        self.server_id = server_id
        super(NotFoundError, self).__init__(self.text)

    def get_code(self):
        return self.status_code

    def to_dict(self):
        return {'message': self.text, 'server_id': self.server_id}

    def __str__(self):
        return repr(self.text)
