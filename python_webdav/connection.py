""" Connection Module
"""
import httplib2
import python_webdav.parse
import python_webdav.file_wrapper as file_wrapper

class Connection(object):
    """ Connection object
    """
    def __init__(self, settings):
        """ Set up the object

            :param settings: The settings required for the connection to
                             be established
            :type settings: Dict

        """
        # Get network settings
        self.username = settings['username']
        self.password = settings['password']
        self.realm = settings['realm']
        self.host = settings['host']
        self.path = settings['path']
        self.port = settings['port']
        self.locks = {}

        # Make an http object for this connection
        self.httpcon = httplib2.Http()
        self.httpcon.add_credentials(self.username, self.password)

    def _send_request(self, request_method, path, body='', headers=None,
                      callback=None):
        """ Send a request over http to the webdav server

            :param request_method: HTML / WebDAV request method
                                   (such as GET or PUT)
            :type request_method: String

            :param path: The path (without host) to the target of the request
            :type path: String

            :param body: Keyword argument. The body of the request method
            :type body: String

            :param headers: Keyword argument. This is where additional headers
                            for the request can be added
            :type headers: Dict

        """
        if not headers:
            headers = {}
        uri = httplib2.urlparse.urljoin(self.host, path)
        try:
            resp, content = self.httpcon.request(uri, request_method,
                                                 body=body, headers=headers)
        except httplib2.ServerNotFoundError:
            raise
        return resp, content

    def send_delete(self, path):
        """ Send a DELETE request

            :param path: The path (without host) to the resource to delete
            :type path: String

        """
        try:
            resp, content = self._send_request('DELETE', path)
            return resp, content
        except httplib2.ServerNotFoundError:
            raise

    def send_get(self, path, headers=None, callback=False):
        """ Send a GET request
            NOTE: callback is not yet implimented. It's purpose is to allow
            the user to specify a callback so that when x percent of the file
            has been retrieved, the callback will be executed. This makes
            allowances for users who may require a progress to be kept track of.

            :param path: The path (without host) to the resource to get
            :type path: String

            :param headers: Additional headers for the request should be added here
            :type headers: Dict

            :param callback: Not yet implimented. This will allow a callback to
                             be added to the method. This is for such uses as
                             keeping track ofupload progress.
            :type callback: Method or Function

        """
        if not headers:
            headers = {}

        try:
            resp, content = self._send_request('GET', path, headers=headers,
                                               callback=callback)
            return resp, content
        except httplib2.ServerNotFoundError:
            raise

    def send_put(self, path, body, headers=None):
        """ This PUT request will put data files onto a webdav server.
            However, please note that due to the way in which httplib2 sends
            files, it is not currently possible to break a file up into chunks
            and read it in. In other words, the whole file has to be read into
            memory for sending. This could be problematic for large files.

            :param path: The path (without host) to the desired file destination
            :type path: String

            :param body: Body of the request. This is the data which to send to
                         the destination file
            :type body: String

            :param headers: Additional headers for the request may be added here
            :type headers: Dict

        """
        if not headers:
            headers = {}

        try:
            resp, content = self._send_request('PUT', path, body=body,
                                               headers=headers)
            return resp, content
        except httplib2.ServerNotFoundError:
            raise

    def send_propfind(self, path, body='', extra_headers=None):
        """ Send a PROPFIND request

            :param path: Path (without host) to the resource from which
                         the properties are required
            :type path: String

            :param body: The body of the request
            :type body: String

            :param extra_headers: Additional headers for the request
                                  may be added here
            :type extra_headers: Dict

        """
        if not extra_headers:
            extra_headers = {}
        try:
            headers = {'Depth': '1'}
            headers.update(extra_headers)
            resp, content = self._send_request('PROPFIND', path, body=body,
                                               headers=headers)
            return resp, content
        except httplib2.ServerNotFoundError:
            raise

    def send_lock(self, path):
        """ Send a LOCK request

            :param path: Path (without host) to the resource to lock
            :type path: String

        """
        try:
            body = '<?xml version="1.0" encoding="utf-8" ?>'
            body += '<D:lockinfo xmlns:D="DAV:"><D:lockscope><D:exclusive/>'
            body += '</D:lockscope><D:locktype><D:write/></D:locktype><D:owner>'
            body += '<D:href>%s</D:href>' % httplib2.urlparse.urljoin(
                self.host, path)
            body += '</D:owner></D:lockinfo>'
            resp, content = self._send_request('LOCK', path, body=body)
            lock_token = LockToken(resp['lock-token'])
            return resp, content, lock_token
        except httplib2.ServerNotFoundError:
            raise

    def send_unlock(self, path, lock_token):
        """ Send an UNLOCK request

            :param path: Path (without host) to the resource to unlock
            :type path: String

            :param lock_token: LockToken object retrived while locking
                               the resource
            :type lock_token: LockToken

        """
        try:
            headers = {'Lock-Token': lock_token.token}
            body = '<?xml version="1.0" encoding="utf-8" ?>'
            body += '<D:lockinfo xmlns:D="DAV:"><D:lockscope><D:exclusive/>'
            body += '</D:lockscope><D:locktype><D:write/></D:locktype><D:owner>'
            body += '<D:href>%s</D:href>' % httplib2.urlparse.urljoin(
                self.host, path)
            body += '</D:owner></D:lockinfo>'
            resp, content = self._send_request('UNLOCK', path, headers=headers,
                                               body=body)
            return resp, content
        except httplib2.ServerNotFoundError:
            raise

    def send_mkcol(self, path):
        """ Send a MKCOL request

            :param path: Path (without host) to the desired place of the
                         new collection
            :type path: String

        """
        try:
            resp, content = self._send_request('MKCOL', path)
            return resp, content
        except httplib2.ServerNotFoundError, err:
            print "Oops, server not found!", err
            raise

    def send_rmcol(self, path):
        """ Send an RMCOL request

            :param path: Path (without host) to the collection to remove
            :type path: String

        """
        try:
            resp, content = self._send_request('DELETE', path)
            return resp, content
        except httplib2.ServerNotFoundError:
            raise

    def send_copy(self, path, destination):
        """ Send a COPY request

            :param path: Path (without host) to the source resource to copy
            :type path: String

            :param destination: Path (without host) to the destination of
                                the copied resource
            :type destination: String

        """
        try:
            full_destination = httplib2.urlparse.urljoin(self.host, destination)
            headers = {'Destination': full_destination}
            resp, content = self._send_request('COPY', path, headers=headers)
            return resp, content
        except httplib2.ServerNotFoundError:
            raise

class LockToken(object):
    """ LockToken object. This is an object that contains information about a
        lock on a resource or collection
    """
    def __init__(self, lock_token):
        """ Make a lock token
        """
        self.token = lock_token


class Property(object):
    """ Property object for storing information about WebDAV properties
    """

    def set_property(self, property_name, property_value=None):
        """ Set property names

            :param property_name: Name of the property
            :type property_name: String

            :param property_value: Value of the named property
            :type property_value: String

        """
        self.__dict__[property_name] = property_value


class Client(object):
    """ This class is for interacting with webdav. Its main purpose is to be
        used by the client.py module but may also be used by developers
        who wish to use more direct webdav access.
    """
    def __init__(self):
        """ Stub
        """
        pass


    def get_properties(self, connection, resource_uri, properties=None):
        """ Get a list of property objects

            :param connection: Connection Object
            :type connection: Connection

            :param resource_uri: the path of the resource / collection minus
                                 the host section
            :type resource_uri: String

            :param properties: list of property names to get. If left empty,
                               will get all
            :type properties: List

            Returns a list of resource objects.

        """
        if not properties:
            properties = []
        # Build body
        body = '<?xml version="1.0" encoding="utf-8" ?>'
        body += '<D:propfind xmlns:D="DAV:">'
        if properties:
            body += '<D:prop>'
            for prop in properties:
                body += '<D:' + prop + '/>'
            body += '</D:prop>'
        else:
            body += '<D:allprop/>'
        body += '</D:propfind>'

        if resource_uri and resource_uri[-1] != '/':
            resource_uri += '/'

        resp, prop_xml = connection.send_propfind(resource_uri, body=body)
        if resp.status >= 200 and resp.status < 300:
            #parser = python_webdav.parse.Parser()
            parser = python_webdav.parse.LxmlParser()
            parser.parse(prop_xml)
            properties = parser.response_objects
            return properties
        else:
            raise httplib2.HttpLib2Error([resp, prop_xml])

    def get_property(self, connection, resource_uri, property_name):
        """ Get a property object

            :param connection: Connection object
            :type connection: Connection

            :param resource_uri: the path of the resource / collection minus
                                 the host section
            :type resource_uri: String

            :param property_name: Property name
            :type property_name: String

            Returns the property value as a string

        """
        property_obj = self.get_properties(connection, resource_uri,
                                           [property_name])[0]
        requested_property_value = getattr(property_obj, property_name, '')
        return requested_property_value

    def get_file(self, connection, resource_uri, local_file_name,
                 extra_headers=None):
        """ Download file

            :param connection: Connection object
            :type connection: Connection

            :param resource_uri: the path of the resource / collection minus
                                 the host section
            :type resource_uri: String

            :param local_file_name: Local file where the resource will be saved
            :type local_file_name: String

            :param extra_headers: Add any extra headers for the request here
            :type extra_headers: Dict

        """
        if not extra_headers:
            extra_headers = {}
        resp, data = connection.send_get(resource_uri, headers=extra_headers)
        file_fd = open(local_file_name, 'w')
        file_fd.write(data)
        file_fd.close()

    def send_file(self, connection, resource_uri, local_file_path,
                  extra_headers=None):
        """ Send file

            :param connection: Connection object
            :type connection: Connection

            :param resource_uri: the path of the resource / collection minus
                                 the host section
            :type resource_uri: String

            :param local_file_path: the path of the local file
            :type local_file_path: String

            :param extra_headers: Additional headers may be added here
            :type extra_headers: Dict

        """

        # The file_wrapper is a file like object. It's purpose is to allow
        # files to be sent in chunks, rather than read into memory as one
        # whole thing. httplib2 currently does not support sending in parts
        # well so this is a work around.
        if not extra_headers:
            extra_headers = {}

        local_file_fd = file_wrapper.FileWrapper(local_file_path, 'r')
        data = local_file_fd.read()
        resp, contents = connection.send_put(resource_uri, data)
        return resp, contents

    def copy_resource(self, connection, resource_path, resource_destination):
        """ Copy a resource from point a to point b on the server

            :param connection: Connection object
            :type connection: Connection

            :param resource_path: Path to the required resource
            :type resource_path: String

            :param resource_destination: Destination of the copied resource
            :type resource_destination: String

        """
        resp, contents = connection.send_copy(resource_path,
                                              resource_destination)
        return resp, contents

    def delete_resource(self, connection, resource_uri):
        """ Delete resource

            :param connection: Connection object
            :type connecton: Connection

            :param resource_uri: URI of the resource
            :type resource_uri: String

        """
        resp, contents = connection.send_delete(resource_uri)
        return resp, contents

# ------------------------- NOT YET IMPLIMENTED ----------------------------- #
    def get_lock(self, resource_uri, connection):
        """ Get a file lock

            :param resource_uri: the path of the resource / collection minus
                                 the host section
            :type resource_uri: String

            :param connection: Connection object
            :type connection: Connection

        """
        lock = connection.send_lock(resource_uri)
        connection.locks[resource_uri] = LockToken(lock)
        return lock

    def release_lock(self, resource_uri, connection):
        """ Release a file lock

            :param resource_uri: the path of the resource / collection minus
                                 the host section
            :type resource_uri: String

            :param connection: Connection object
            :type lock_object: Connection

        """
        # If there's not a lock recorded, return false for now. We should
        # really raise an exception to make it more obvious.
        if not connection.locks.get(resource_uri):
            return False
        resp, cont = connection.send_unlock(resource_uri,
                                            connection.locks[resource_uri])
        # remove from our dictionary if the lock was released successfully
        if resp >= 200 and resp < 300:
            del connection.locks[resource_uri]
        return resp
