# ##########
#
#  This is an example program, meant to show some basic usage of the Client
#  module and its classes.
#
#  It is part of the python-webdav example materials and documentation.
#
# ##########

import python_webdav.client

class Example(object):
    def get_example_file(self):
        """ This example would set up a connection and download a file from
            http://example.net/myWebDAV/example1.txt

        """

        # Make the client object. 'http://example.net/' is the webdav server
        # url and '/myWebDAV' is the root path for the webdav enabled server.
        example_client = python_webdav.client.Client('http://example.net/',
                                                     '/myWebDAV')

        # Set up the connection. Pass in any authentication details here.
        example_client.set_connection(username='user123', password='pass')

        # Download the required file. Will write the file to a local file of
        # the same name. dest_path may be given as a keyword argument if the
        # file is to be downloaded to a specific location.
        response = example_client.download_file('example1.txt')


if __name__ == '__main__':
    pass
