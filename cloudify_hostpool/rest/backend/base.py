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
    """ Interface for business logic layer of host acquisition and release"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def list_hosts(self):
        """
        List all allocated hosts.

        :return: host(dictionaries)
        :rtype: list of 'dict'
        """

    @abc.abstractmethod
    def acquire_host(self):
        """
        Host acquisition - schedule host acquisition first running host,
        reserve it, if is still responsive it add acquisition host_id to
        host and return it.

        :raises NoResourcesError(HostPoolHTTPException): if no available hosts
        found
        :return: host(dictionary) with host_id not None
        :rtype: dict
        """

    @abc.abstractmethod
    def release_host(self, host_id):
        """
        Release host with acquisition id given that is no longer needed.
        Remove acquisition id (host_id) from given host.

        :raises NotFoundError(HostPoolHTTPException): if there is no host with
        given id
        :return: host(dictionary) that has been released
        :rtype: dict
        """

    @abc.abstractmethod
    def get_host(self, host_id):
        """
        Retrieve host details.

        :raises NotFoundError(HostPoolHTTPException): if there is no host with
        given id
        :return: requested host(dictionary) with host_id given
        :rtype: dict
        """
