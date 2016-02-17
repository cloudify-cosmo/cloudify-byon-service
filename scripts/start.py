'''
    lifecycle.Start
    ~~~~~~~~~~~~~~~
    Starts the Cloudify Host-Pool Service
'''
import pkgutil
import os
from time import sleep
from string import Template
import tempfile
from subprocess import Popen, PIPE, call
import requests
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError
from cloudify_hostpool.logger import get_hostpool_logger

BASE_DIR = ctx.instance.runtime_properties.get('working_directory')
VIRT_DIR = os.environ.get('VIRTUALENV')
SVC_DEBUG = ctx.node.properties.get('gunicorn_debug')
CONFIG_PATH = ctx.instance.runtime_properties.get('config_path')
HOST = ctx.instance.host_ip
PORT = ctx.node.properties.get('port')
SCHEME = 'http'
ENDPOINT = '%s://%s:%s' % (SCHEME, HOST, PORT)
SVC_NAME = 'cloudify-hostpool'
INIT_PATH = '/etc/init.d/%s' % SVC_NAME


def cmd_exists(cmd, logger):
    '''Test to see if a command exists on the system'''
    logger.debug('Checking if command "%s" exists', cmd)
    retval = call("type " + cmd, shell=True, stdout=PIPE, stderr=PIPE) == 0
    logger.debug('Command "%s" %s found', cmd, 'was' if retval else 'was not')
    return retval


def download_service(logger):
    '''Downloads the service file and pre-processes'''
    # Grab the init script from the package
    logger.info('Downloading Host-Pool service init script')
    init_data = pkgutil.get_data('cloudify_hostpool',
                                 'resources/service_init.sh')
    if not init_data:
        NonRecoverableError('Could not download Host-Pool service init script '
                            'from cloudify_hostpool:resources/service_init.sh')

    # Pre-process the script (replace defaults)
    logger.debug('Replacing default values in init script')
    tmpl = Template(init_data)
    init_data = tmpl.safe_substitute({
        'TMPL_BASE_DIR': BASE_DIR,
        'TMPL_VIRT_DIR': VIRT_DIR,
        'TMPL_SVC_LOG_LEVEL': 'DEBUG' if SVC_DEBUG else 'INFO'
    })
    logger.debug('Init script contents: %s', init_data)

    # Write the init script data to a temporary file
    logger.debug('Creating temporary init script file')
    (temp_fd, temp_name) = tempfile.mkstemp()
    logger.debug('Temporary file created: %s', temp_name)
    os.write(temp_fd, init_data)
    os.close(temp_fd)
    return temp_name


def set_service_permissions(svc, logger):
    '''Set the correct access, owner, and group for the service'''
    # Set init script as executable
    logger.debug('Setting init script as executable')
    os.chmod(svc, os.stat(svc).st_mode | 0o111)
    logger.debug('Init script permissions: %s',
                 oct(os.stat(svc).st_mode))

    # Set init script owner to root
    logger.debug('(sudo) Setting owner of "%s" to "root:root"', svc)
    proc = Popen(['sudo', 'chown', 'root:root', svc], stderr=PIPE)
    err = proc.communicate()
    if proc.returncode:
        logger.error('Error setting owner of "%s": %s', svc, err)
        NonRecoverableError('Exception: %s' % err)


def install_service(svc, logger):
    '''Installs the service into /etc/init.d/'''
    logger.debug('(sudo) Moving "%s" to "%s"', svc, INIT_PATH)
    proc = Popen(['sudo', 'mv', svc, INIT_PATH], stderr=PIPE)
    err = proc.communicate()
    logger.debug('Operation returned code "%s"', proc.returncode)
    if proc.returncode:
        logger.error('Error moving init script to /etc/init.d/')
        NonRecoverableError('Exception: %s' % err)


def start_service(logger):
    '''Starts the service'''
    logger.info('(sudo) Starting the Host-Pool service')
    proc = Popen(['sudo', 'service', SVC_NAME, 'start'], stderr=PIPE)
    err = proc.communicate()
    logger.debug('Service returned code "%s"', proc.returncode)
    if proc.returncode:
        logger.error('Error starting Host-Pool service: %s', err)


def set_service_on_boot(logger):
    '''Sets up the service to start on system boot'''
    # Enable service on boot for Red Hat
    logger.info('(sudo) Enabling the Host-Pool service on boot')

    # Red Hat
    if cmd_exists('chkconfig', logger):
        proc = Popen(['sudo', 'chkconfig', '--add', SVC_NAME],
                     stderr=PIPE)
    # Debian
    elif cmd_exists('update-rc.d', logger):
        proc = Popen(['sudo', 'update-rc.d', SVC_NAME, 'defaults'],
                     stderr=PIPE)
    # Unknown
    else:
        NonRecoverableError('Neither chkconfig or update-rc.d was found')

    if proc:
        err = proc.communicate()
        logger.debug('Command returned code "%s"', proc.returncode)
        if proc.returncode:
            logger.error('Error enabling Host-Pool service on boot: %s', err)


def test_service_liveness(logger):
    '''Tests if the service is running correctly'''
    max_attempts = 20
    for i in range(max_attempts):
        logger.info('[Attempt %s/%s] Liveness detection check',
                    i, max_attempts)
        logger.debug('GET %s/hosts', ENDPOINT)
        try:
            req = requests.get('%s/hosts' % ENDPOINT)
            logger.debug('HTTP status: %s', req.status_code)
            if req.status_code == 200:
                logger.info('Host-Pool service is alive')
                break
            else:
                logger.error('Bad HTTP status returned: %s', req.status_code)
        except requests.exceptions.RequestException as ex:
            logger.warn('Exception raised connecting to service: %s', ex)
        logger.warn('Waiting 2 seconds before retrying')
        sleep(2)


def main():
    '''Entry point'''
    logger = get_hostpool_logger('start',
                                 debug=ctx.node.properties.get('debug'))

    # Make sure VIRTUALENV is set
    if not VIRT_DIR:
        NonRecoverableError('VIRTUALENV environment variable must be set!')

    # Grab the init script from the package
    svc_tmp = download_service(logger)
    # Set the correct service permissions
    set_service_permissions(svc_tmp, logger)
    # Move the init script to /etc/init.d/
    install_service(svc_tmp, logger)
    # Start the service
    start_service(logger)
    # Test if the service is alive
    test_service_liveness(logger)
    # Enable the service to start on boot
    set_service_on_boot(logger)
    # Set runtime properties
    ctx.instance.runtime_properties['service_name'] = SVC_NAME
    ctx.instance.runtime_properties['endpoint'] = ENDPOINT

main()
