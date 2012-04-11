"""
Client Module
=============

"""
import os
import urllib2
import python_webdav.connection as conn
import python_webdav.file_wrapper as file_wrapper
from array import array

class Client(object):
    """ This is used for accessing a WebDAV service using similar commands
        that might be found in a CLI
    """

    def __init__(self, webdav_server_uri, webdav_path='.', port=80, realm=''):
        """

The Client module is not yet ready for use. The purpose of this module is to
make WebDAV use easier. The Connection.Client object is for lower level use
while this top level module will hopefully aid in quicker development.

        """
        self._connection_settings = dict(host=webdav_server_uri,
                                         path=webdav_path,
                                         port=port, realm=realm)
        path = self._connection_settings['path']
        if path[-1] != '/' and path != '.':
            self._connection_settings['path'] += '/'
        self.connection = None
        self.client = None

    def rmdir(self, dir_path):
        """ Remove a directory

            :param dir_path: This should be either a relative path or an
                             absolute path to the collection to remove
            :type dir_path: String

        """
        if not dir_path.startswith('/'):
            dir_path = self.connection.path + '/' + dir_path
        self.connection.send_rmcol(dir_path)

    def set_connection(self, username='', password=''):
        """ Set up the connection object

            :param username: Username if authentication is required for the connection
            :type username: String

            :param password: Password if authentication is required for the connection
            :type password: String

        """
        self._connection_settings['username'] = username
        self._connection_settings['password'] = password
        self.connection = conn.Connection(self._connection_settings)
        self.client = conn.Client()

    def download_file(self, file_path, dest_path='.'):
        """ Download a file from file_path to dest_path

            :param file_path: Path to the resource to download
            :type file_path: String

            :param dest_path: Path to where the downloaded file should be saved
            :type dest_path: String

        """
        resource_path = urllib2.urlparse.urljoin(self.connection.path,
                                                 file_path.strip('/'))
        resp, content = self.connection.send_get(resource_path)
        file_name = os.path.basename(file_path)
        write_to_path = os.path.join(dest_path, file_name)

        try:
            file_fd = open(write_to_path, 'wb')
            file_fd.write(content)
        except IOError:
            raise
        finally:
            file_fd.close()

        return resp, content

    def chdir(self, directory):
        """ Change directory from whatever current dir is to directory specified

            :param directory: Directory to change to
            :type directory: String

        """
        # Make sure there's a leading '/'
        if not self.connection.path.startswith('/'):
            self.connection.path = '/' + self.connection.path
        self.connection.path = os.path.realpath(
            os.path.join(self.connection.path, directory))

    def mkdir(self, path):
        """ Make a directory (collection). If path does not start with '/'
            it is assumed to be relative to the current working directory.

            :param path: Path of the directory to create
            :type path: String

        """
        if not path.startswith('/'):
            path = self.connection.path + '/' + path
        self.connection.send_mkcol(path)

    def ls(self, path='', list_format=('F', 'C', 'M'), separator='\t',
           display=True):
        """
            :param path: Path of the directory to list
            :type path: String

            :param list_format: This is the format for the directory listing

            The format symbols are:
                * T - Type (resourcetype)
                * D - Date Time (creationdate)
                * F - Filename (href)
                * M - Last modified time (getlastmodified)
                * A - Attributes (executable)
                * E - ETag (getetag)
                * C - Content type (getcontenttype)

            :type list_format: List

            :param separator: Separator to use for formatting output
            :type separator: String

            :param display: Whether or not to print the output
            :type display: Boolean

        """
        # Format Map
        format_map = {'T': 'resourcetype',
                      'D': 'creationdate',
                      'F': 'href',
                      'M': 'getlastmodified',
                      'A': 'executable',
                      'E': 'getetag',
                      'C': 'getcontenttype'}

        # Get the properties for the given path
        if not path:
            path  = self.connection.path
        props = self.client.get_properties(self.connection, path)
        property_lists = []
        for prop in props:
            format_string = ''
            formatted_list = []
            for symbol in list_format:
                str_prop = getattr(prop, format_map[symbol], None)
                if not str_prop:
                    str_prop = ''
                if symbol == 'E':
                    str_prop = str_prop.strip('"')
                formatted_list.append(str_prop)
            property_lists.append(formatted_list)
            format_string = separator.join(formatted_list)
            if display:
                print format_string
        return property_lists

# ------------ EXPERIMENTAL -------------- #
    def pwd(self):
        """ Return the working directory
        """
        if self.connection:
            return self.connection.path
        else:
            return None

    def upload_file(self, src_file, path=None):
        """ Upload a file to the server

            :param src_file: File to be sent.
            :type src_file: file or String

        """

        # Is the file a file name or file object?
        if hasattr(src_file, 'read') and not isinstance(src_file, array):
            # It's an object. In order to avoid complications with httplib2,
            # close file and reopen using the file_wrapper object
            file_name = src_file.name
            src_file.close()
        else:
            file_name = src_file
        fileobj = file_wrapper.FileWrapper(file_name, 'rb')

        if not path:
            path = os.path.join(self.connection.path, file_name)

        resp, content = self.connection.send_put(path, fileobj)
        fileobj.close()

        return resp, content