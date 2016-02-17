'''
    hostpool.logger
    ~~~~~~~~~~~~~~~
    Creates the Cloudify Host-Pool Service logger
'''
import logging
import os
from cloudify import ctx

BASE_DIR = ctx.instance.runtime_properties.get('working_directory')
DEBUG_LOG = os.path.join(BASE_DIR, 'debug.log')


def get_hostpool_logger(mod, debug=False):
    '''Configures a host-pool deployment logger'''
    logger = ctx.logger.getChild(mod)

    if debug:
        logger.setLevel(logging.DEBUG)

        # Limit the stdout output to INFO (it's NOTSET by default)
        # logger.parent.handlers[0].setLevel(logging.INFO)

        # Make sure the debug log file exists
        if not os.path.exists(DEBUG_LOG):
            # Create the directory path if needed
            if not os.path.isdir(os.path.dirname(DEBUG_LOG)):
                os.makedirs(os.path.dirname(DEBUG_LOG))
            # Create the file & update timestamp
            with open(DEBUG_LOG, 'a'):
                os.utime(DEBUG_LOG, None)

        # Create our log handler for the debug file
        file_handler = logging.FileHandler(DEBUG_LOG)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logger.parent.handlers[0].formatter)
        logger.addHandler(file_handler)

    return logger
