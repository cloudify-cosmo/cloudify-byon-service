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


class AbstractRestBackend(object):
    """ Interface for business logic layer of server acquisition and release"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def list_servers(self):
        """
        List all allocated servers.

        :return: server(dictionaries)
        :rtype: list of 'dict'
        """

    @abc.abstractmethod
    def acquire_server(self):
        """
        Server acquisition - schedule server acquisition first running server,
        reserve it, if is still responsive it add acquisition server_id to
        server and return it.

        :raises NoResourcesError(HostPoolHTTPException): if no available
        servers found
        :return: server(dictionary) with server_id not None
        :rtype: dict
        """

    @abc.abstractmethod
    def release_server(self, server_id):
        """
        Release server with acquisition id given that is no longer needed.
        Remove acquisition id (server_id) from given server.

        :raises NotFoundError(HostPoolHTTPException): if there is no server
         with given id
        :return: server(dictionary) that has been released
        :rtype: dict
        """

    @abc.abstractmethod
    def get_server(self, server_id):
        """
        Retrieve server details.

        :raises NotFoundError(HostPoolHTTPException): if there is no server
        with given id
        :return: requested server(dictionary) with server_id given
        :rtype: dict
        """
