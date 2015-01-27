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
import abc


class DBinterface(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def set_default_auth(self, auth):
        """Set default auth(dictionary) with
           credentials(username and password or keyfile) set in config"""

    @abc.abstractmethod
    def get_servers(self):
        """Return all servers in database"""

    @abc.abstractmethod
    def add_server(self, server):
        """Add server(dictionary) to database"""

    @abc.abstractmethod
    def delete_server(self, server_id):
        """Delete server from database using its acquisition id"""

    @abc.abstractmethod
    def change_server_status(self, server_global_id, status_from, status_to):
        """Change server status in database from status from to status to"""

    @abc.abstractmethod
    def acquire_server(self):
        """Return first active server(dictionary)
           and change its status to 'reserved'"""

    @abc.abstractmethod
    def get_server(self, server_id):
        """Get specific server identified by given id'"""
