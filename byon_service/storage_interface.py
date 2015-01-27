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


class StorageInterface(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def list_servers(self):
        """Return all servers in database that are allocated"""

    @abc.abstractmethod
    def add_server(self, server):
        """Add server(dictionary) to database"""

    @abc.abstractmethod
    def change_server_status(self, server_global_id, reserved, living):
        """Change server status in database for reserved and living fields"""

    @abc.abstractmethod
    def acquire_server(self):
        """Return first active server(dictionary)
           and change its status to 'reserved'"""

    @abc.abstractmethod
    def get_server(self, server_id):
        """Get specific server identified by given allocation id(server_id)'"""
