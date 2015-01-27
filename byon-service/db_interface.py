import abc


class DBinterface(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def set_default_auth(self, auth):
        """Set default auth(dictionary) with
            credentials(username and password or keyfile) set in config"""

    @abc.abstractmethod
    def get_servers(self):
        """Return all servers in database"""

    @abc.abstractmethod
    def add_server(self, server):
        """Add server(dictionary) to database"""

    @abc.abstractmethod
    def delete_server(self, server_global_id):
        """Delete server from database"""

    @abc.abstractmethod
    def update_server(self, server):
        """Update server in database"""

    @abc.abstractmethod
    def get_server(self, server_id):
        """Retrieve specific server identified by server_id"""
