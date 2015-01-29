###############################################################################
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################


'''`backend.ping`
Efficiently scans given endpoints (pairs of hosts with ports) if they
are connectible.

The internal mechanism opens a large number of socket file descriptors
with O_NONBLOCK flag set (see: socket(2), fcntl(2), connect(2)),
and concurrently waits for each socket's state changes with pselect
(see: select(2)).

File descriptors creation is limited, so that the soft limit should
not be exceeded (see: getrlimit(2)). If a large collection of endpoints
is being scanned, it is split into smaller chunks. If the number
of open file descriptors is dangerously high, scanning is being
performed sequentially.
'''


import copy
import errno
import fcntl
import itertools
import os
import resource
import select
import socket


_MAGIC_NUMBER_DEFAULT_PORT = 22
_MAGIC_NUMBER_SPLIT_LOWER_THRESHOLD = .25
_MAGIC_NUMBER_SPLIT_UPPER_THRESHOLD = .75


def scan(endpoints, default_port = _MAGIC_NUMBER_DEFAULT_PORT):
    '''Checks if given endpoints are connectible

    :return: a dictionary of (host, port): bool is open.
    :param endpoints: a collection of tuples (host, port) or just host.
    :param default_port: if port not set explicitly it will be defaulted
            to this value.
    '''
    results = {}
    filled_endpoints = _fill_endpoints(endpoints, default_port)
    for e in _split(filled_endpoints):
        r = _scan(e)
        results.update(r)
    return results


def _get_number_of_open_file_descriptors():
    return len(os.listdir('/proc/{0}/fd'.format(str(os.getpid()))))


def _get_file_descriptor_resource_limit():
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    return soft


def _create_socket_2(address_family, socket_type, protocol, address_tuple):
    try:
        sock = socket.socket(address_family, socket_type, protocol)
    except socket.error:
        return None, False
    sock_fd = sock.fileno()
    fd_flags = fcntl.fcntl(sock_fd, fcntl.F_GETFL)
    fd_flags |= os.O_NONBLOCK
    fcntl.fcntl(sock_fd, fcntl.F_SETFL, fd_flags)
    try:
        sock.connect(address_tuple)
    except socket.error as e:
        if e.errno == errno.EINPROGRESS:
            return sock, False
        else:
            sock.close()
            return None, False
    else:
        sock.close()
        return None, True


def _create_socket(struct_getaddrinfo):
    return _create_socket_2(struct_getaddrinfo[0],
                              struct_getaddrinfo[1],
                              struct_getaddrinfo[2],
                              struct_getaddrinfo[4])


def _wait_for_any_change(socket_fds):
    select_results = select.select(socket_fds,
                                   socket_fds,
                                   socket_fds,
                                   None)
    return list(set(itertools.chain.from_iterable(select_results)))


def _check_connection(sock):
    try:
        sock.getpeername()
    except socket.error as e:
        if e.errno != errno.ENOTCONN:
            raise
        result = False
    else:
        result = True
    finally:
        sock.close()
    return result


def _scan(endpoints):
    results = {}
    sockets = {}
    try:
        for host, port in endpoints:
            getaddrinfo_results = socket.getaddrinfo(host,
                                                     port,
                                                     socket.AF_UNSPEC,
                                                     socket.SOCK_STREAM)
            for r in getaddrinfo_results:
                sock, is_open = _create_socket(r)
                if is_open:
                    results[host, port] = True
                    break
                elif sock:
                    # Yes, a nested tuple.
                    sockets[sock.fileno()] = sock, (host, port)
                    break
            # If not broken...
            else:
                results[host, port] = False
        while sockets:
            fds = _wait_for_any_change(sockets.keys())
            for fd in fds:
                sock, host_and_port = sockets[fd]
                results[host_and_port] = _check_connection(sock)
                del sockets[fd]
    finally:
        for s, _ in sockets.itervalues():
            s.close()
        sockets.clear()
    return results


def _split(endpoints):
    '''A generator yielding parts of the given endpoint list split
    in such way, that soft maximum open file descriptor resource
    limit **should** not be exceeded.'''
    i = 0
    while i < len(endpoints):
        limit = _get_file_descriptor_resource_limit()
        fd_num = _get_number_of_open_file_descriptors()
        beg = i
        l = _MAGIC_NUMBER_SPLIT_LOWER_THRESHOLD
        u = _MAGIC_NUMBER_SPLIT_UPPER_THRESHOLD
        i += (1 if fd_num >= l * limit else int(u * limit))
        yield endpoints[beg : i]


def _fill_endpoints(endpoints, default_port):
    return [e if isinstance(e, tuple)
            else (e, default_port)
            for e in endpoints]
