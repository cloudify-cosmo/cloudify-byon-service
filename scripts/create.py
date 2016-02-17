'''
    lifecycle.Create
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    Creates the Cloudify Host-Pool Service
'''
import os
from subprocess import Popen, PIPE
from cloudify import ctx
from cloudify.exceptions import RecoverableError

BASE_DIR = os.path.join(os.path.expanduser('~'), 'hostpool')


def install_requirements():
    '''Install required Python packages'''
    reqs = [
        'gunicorn==19.4.5',
        'pyyaml==3.11',
        ctx.node.properties.get('source')
    ]

    for req in reqs:
        ctx.logger.info('Installing Python package "%s"', req)
        proc = Popen(['pip', 'install', req], stderr=PIPE)
        err = proc.communicate()
        if proc.returncode:
            ctx.logger.error('Installing Python package "%s" failed', req)
            RecoverableError(message=err, retry_after=2)


def main():
    '''Entry point'''
    try:
        ctx.logger.info('Creating working directory: "%s"', BASE_DIR)
        if not os.path.isdir(BASE_DIR):
            os.makedirs(BASE_DIR)
    except OSError as ex:
        ctx.logger.error('Error making directory "%s"', BASE_DIR)
        RecoverableError(message=ex, retry_after=2)

    ctx.logger.info('Installing required Python packages')
    install_requirements()

    ctx.logger.info('Setting runtime_property "working_directory" to "%s"',
                    BASE_DIR)
    ctx.instance.runtime_properties['working_directory'] = BASE_DIR


main()
