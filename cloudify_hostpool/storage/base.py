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

    """
    Interface for storage transactional operations.

    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_servers(self, **filters):

        """
        Retrieves servers in the database that fit the given filters.
        If no filters are supplied, all servers are returned.

        :param filters: a dictionary of filters to search by.
        :return A list of servers.
        :rtype list of `dict`

        """
        pass

    @abc.abstractmethod
    def add_server(self, server):

        """
        Add a server to the database.

        :param server: The server to add (dictionary).

        """
        pass

    @abc.abstractmethod
    def update_server(self, global_id, server):

        """
        Update a server with new values.

        :param global_id: The global id of the server.
        :param server: The server dictionary containing the new values.

        :return (False, None) if no change occurred, (True, server) otherwise.
        :rtype (bool, dict)

        """
        pass

    @abc.abstractmethod
    def reserve_server(self, **filters):

        """
        Return first active server that answers the filters
        and change its status to 'reserved'.

        :param filters: a dictionary of filters to search by.
        :return The server.
        :rtype dict

        """
        pass

    @abc.abstractmethod
    def get_server(self, **filters):

        """
        Return the first server data that answers the filters.

        :param filters: a dictionary of filters to be applied on the result.
        :return The server.
        :rtype dict

        """
        pass
