'''
    lifecycle.Delete
    ~~~~~~~~~~~~~~~~
    Deletes the Cloudify Host-Pool Service
'''
from shutil import rmtree
from cloudify import ctx
from cloudify_hostpool.logger import get_hostpool_logger

BASE_DIR = ctx.instance.runtime_properties.get('working_directory')


def main():
    '''Entry point'''
    logger = get_hostpool_logger('delete',
                                 debug=ctx.node.properties.get('debug'))
    # Delete working directory
    logger.info('Deleting directory "%s"', BASE_DIR)
    rmtree(BASE_DIR, ignore_errors=True)


main()
