import itertools

import backend.ping


_START_PORT = 3
_END_PORT = 50000 + _START_PORT


if __name__ == '__main__':
    r = backend.ping.scan(
        zip(itertools.repeat('localhost'),
            xrange(_START_PORT, _END_PORT))
    )
    print 'scanned: {0}; open: {1}'.format(len(r),
                                           ', '.join(str(hp[1])
                                                     for hp, a in r.iteritems()
                                                     if a))
