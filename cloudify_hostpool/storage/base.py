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
    def get_hosts(self, **filters):

        """
        Retrieves hosts in the database that fit the given filters.
        If no filters are supplied, all hosts are returned.

        :param filters: a dictionary of filters to search by.
        :return A list of hosts.
        :rtype list of `dict`

        """
        pass

    @abc.abstractmethod
    def add_host(self, host):

        """
        Add a host to the database.

        :param host: The host to add (dictionary).

        """
        pass

    @abc.abstractmethod
    def update_host(self, global_id, host):

        """
        Update a host with new values.

        :param global_id: The global id of the host.
        :param host: The host dictionary containing the new values.

        :return  None if no change occurred, host otherwise.
        :rtype  dict

        """
        pass

    @abc.abstractmethod
    def reserve_host(self, global_id):

        """
        Change status of the given host(global_id) to 'reserved'.

        :param global_id: The global id of the host.
        :return False if host has been already reserved, True otherwise.
        :rtype boolean

        """
        pass

    @abc.abstractmethod
    def get_host(self, **filters):

        """
        Return the first host data that answers the filters.

        :param filters: a dictionary of filters to be applied on the result.
        :return The host.
        :rtype dict

        """
        pass
