'''
    lifecycle.Stop
    ~~~~~~~~~~~~~~
    Stops the Cloudify Host-Pool Service
'''
from subprocess import Popen, PIPE
from cloudify import ctx
from cloudify_hostpool.logger import get_hostpool_logger

SVC_NAME = 'cloudify-hostpool'


def stop_service(logger):
    '''Stops the service'''
    logger.info('(sudo) Stopping the Host-Pool service')
    proc = Popen(['sudo', 'service', SVC_NAME, 'stop'], stderr=PIPE)
    err = proc.communicate()
    logger.debug('Service returned code "%s"', proc.returncode)
    if proc.returncode:
        logger.error('Error stopping Host-Pool service: %s', err)


def main():
    '''Entry point'''
    logger = get_hostpool_logger('stop',
                                 debug=ctx.node.properties.get('debug'))
    # Delete working directory
    logger.info('Stopping service "%s"', SVC_NAME)
    stop_service(logger)

main()
