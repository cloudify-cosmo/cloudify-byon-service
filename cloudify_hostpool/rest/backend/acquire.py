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


import uuid

from cloudify_hostpool.backend import scan


def acquire(db):
    '''"Creates" (acquires) a host.

    :return: host dict if successful, None otherwise.
    :param db: host database.
    '''
    for host in _aquisition_gen(db):
        if not db.reserve_host(host['global_id']):
            continue
        try:
            host = _check_if_alive(db, host)
        except:
            db.update_host(host['global_id'], {'reserved': False})
            raise
        if not host['alive']:
            db.update_host(host['global_id'], {'reserved': False})
            continue
        host = db.update_host(host['global_id'],
                              {'host_id': str(uuid.uuid4()),
                               'reserved': False})
        return host
    return None


def _aquisition_gen(db):
    for alive in True, False:
        for host in db.get_hosts(reserved=False, alive=alive):
            if host.get('host_id') is None:
                yield host


def _check_if_alive(db, host):
    address, port = host['host'], host['port']
    results = scan.scan([(address, port)])
    is_alive = results[address, port]
    return db.update_host(host['global_id'], {'alive': is_alive})
