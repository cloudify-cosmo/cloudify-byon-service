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


class AbstractStorage(object):
    """ Interface for storage transactional operations """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def list_servers(self, **kwargs):
        """ Return all servers in database filtered by given fields
        if no kwargs(filters) given, return all servers"""

    @abc.abstractmethod
    def add_server(self, server):
        """ Add server(dictionary) to database"""

    @abc.abstractmethod
    def update_server(self, server, **kwargs):
        """ Update server in storage for given fields,
        return False if no change occurred, True otherwise"""

    @abc.abstractmethod
    def reserve_server(self, server):
        """ Return first active server(dictionary) and change its status
        to 'reserved'."""

    @abc.abstractmethod
    def get_server(self, **kwargs):
        """ Return data of specific server identified by given field"""
