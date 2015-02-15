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


class HostPoolHTTPException(Exception):
    """  An error raised by service modules to handle errors in REST API"""

    def get_code(self):
        pass

    def to_dict(self):
        pass

    def __str__(self):
        pass


class NoResourcesError(HostPoolHTTPException):
    """Raised when there is no hosts left to be acquired"""

    def __init__(self):
        self.status_code = 515
        self.text = "Cannot acquire host. " \
                    "The pool is empty or all hosts are in use."
        super(NoResourcesError, self).__init__(self.__str__)

    def get_code(self):
        return self.status_code

    def to_dict(self):
        return {'message': self.text}

    def __str__(self):
        return repr(self.text)


class NotFoundError(HostPoolHTTPException):
    """Raised when there is no host with requested id"""

    def __init__(self, host_id):
        self.status_code = 404
        self.text = "Cannot find requested host. "
        self.host_id = host_id
        super(NotFoundError, self).__init__(self.__str__)

    def get_code(self):
        return self.status_code

    def to_dict(self):
        return {'message': self.text, 'host_id': self.host_id}

    def __str__(self):
        return repr(self.text)


class ConfigError(Exception):
    """Raised when there is some error in configuration"""
    def __init__(self, message):
        super(ConfigError, self).__init__(message)


class DBError(Exception):
    """Raised when there is some error in database"""
    def __init__(self, message):
        super(DBError, self).__init__(message)


class DBLockedError(DBError):
    """Raised when the database is locked"""
    def __init__(self):
        super(DBLockedError, self).__init__("Database is locked")
