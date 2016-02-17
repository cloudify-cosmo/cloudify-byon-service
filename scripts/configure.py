'''
    lifecycle.Configure
    ~~~~~~~~~~~~~~~~~~~
    Configures the Cloudify Host-Pool Service
'''
import os
import json
import yaml
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError
from cloudify_hostpool.logger import get_hostpool_logger

BASE_DIR = ctx.instance.runtime_properties.get('working_directory')
POOL_CFG_PATH = os.path.join(BASE_DIR, 'pool.yaml')
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')


def download_key_files(cfg, logger):
    '''Downloads all key files to the service directory

    :param dict cfg: Host-Pool configuration file data
    :returns: List of blueprint-relative paths to the key files
    '''
    keys = set()

    # Get the default key (if specified)
    logger.debug('Checking for a default key file')
    default_key = cfg.get('default', {}).get('auth', {}).get('keyfile')
    logger.debug('Default key file: "%s"', default_key)
    if default_key:
        keys.add(default_key)

    # Create a unique list of keys to download
    for host in cfg.get('hosts'):
        logger.debug('Checking key file for host "%s"', host.get('host'))
        key = host.get('auth', {}).get('keyfile')
        if not key:
            logger.debug('Host "%s" does not specify a key file',
                         host.get('host'))
        else:
            logger.debug('Host "%s" specified key file "%s"',
                         host.get('host'), key)
            keys.add(key)

    # Download the key files to the service directory
    for key_file in keys:
        target_path = os.path.join(BASE_DIR, key_file)
        directory = os.path.dirname(target_path)
        os.makedirs(directory)
        logger.debug('Downloading key file "%s" to path "%s"',
                     key_file, target_path)
        ctx.download_resource(key_file, target_path)

    return keys


def create_config_file(logger):
    '''Creates a JSON config file for the service to use'''
    config_json = {
        'pool': POOL_CFG_PATH
    }
    logger.debug('Creating service configuration file: "%s"',
                 json.dumps(config_json, indent=2))
    with open(CONFIG_PATH, 'w') as f_cfg:
        json.dump(config_json, f_cfg, indent=2)


def main():
    '''Entry point'''
    logger = get_hostpool_logger('configure',
                                 debug=ctx.node.properties.get('debug'))

    if not ctx.node.properties.get('pool'):
        NonRecoverableError('Configuration file for the Host-Pool '
                            'service was not specified')

    logger.debug('Downloading host-pool configuration file "%s" to "%s"',
                 ctx.node.properties.get('pool'), POOL_CFG_PATH)
    ctx.download_resource(ctx.node.properties.get('pool'),
                          target_path=POOL_CFG_PATH)

    if not os.path.exists(POOL_CFG_PATH):
        NonRecoverableError('Configuration file for the Host-Pool '
                            'service could not be downloaded')

    # Load our configuration data
    with open(POOL_CFG_PATH) as f_cfg:
        try:
            logger.info('Loading Host-Pool configuration data')
            cfg = yaml.load(f_cfg)
            logger.info('Importing host key files from blueprint')
            download_key_files(cfg, logger)
            logger.info('Creating service configuration file')
            create_config_file(logger)
        except yaml.YAMLError as ex:
            logger.error('Exception: %s', ex)
            NonRecoverableError('Configuration file for the Host-Pool '
                                'service is not valid YAML')

    logger.info('Setting runtime_property "config_path" to "%s"',
                CONFIG_PATH)
    ctx.instance.runtime_properties['config_path'] = CONFIG_PATH


main()
