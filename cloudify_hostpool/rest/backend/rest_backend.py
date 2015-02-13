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

import acquire
from cloudify_hostpool.config import config
from cloudify_hostpool.storage import sqlite
from cloudify_hostpool.rest.backend import base
from cloudify_hostpool import exceptions


class RestBackend(base.AbstractRestBackend):
    """
    Implementation of AbstractRestBackend
    """

    def __init__(self, file_name, db_file_name):
        self.storage = sqlite.SQLiteStorage(db_file_name)
        if self.storage.db_creation_successful:
            self.__load_config(file_name)

    def list_hosts(self):
        hosts = self.storage.get_hosts(
            [sqlite.Filter('host_id', None, sqlite.Filter.IS_NOT)])
        # further should be here some translation
        # to status when we decide what status should be like
        return hosts

    def acquire_host(self):
        host = acquire.acquire(self.storage)
        if host is None:
            raise exceptions.NoResourcesError()
        return host

    def release_host(self, host_id):
        host = self.storage.get_host([sqlite.Filter('host_id', host_id)])
        if host is None:
            raise exceptions.NotFoundError(host)
        updated_host = self.storage.update_host(host['global_id'],
                                                dict(host_id=None))
        # further should be here some translation
        # to status when we decide what status should be like
        return updated_host

    def get_host(self, host_id):
        host = self.storage.get_host([sqlite.Filter('host_id', host_id)])
        if host is None:
            raise exceptions.NotFoundError(host_id)
        # further should be here some translation
        # to status when we decide what status should be like
        return host

    def __load_config(self, file_name):
        hosts = config.load_config(file_name)
        for host in hosts:
            self.storage.add_host(host)
