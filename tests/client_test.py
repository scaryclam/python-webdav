import unittest
import os
import re
import mock
from datetime import datetime

import python_webdav.client as webdav_client

class TestClient(unittest.TestCase):
    """ Test case for the client
    """
    def setUp(self):
        """ setUp
        """
        self.client = webdav_client.Client('http://localhost:8008/webdav',
                                           webdav_path = '.',
                                           realm = 'test-realm',
                                           port = 80)
        self.client.set_connection(username='wibble', password='fish')

    def tearDown(self):
        """ tearDown
        """
        pass

    def test_download_file(self):
        """ Download a simple file
        """
        file_path = 'webdav/test_file1.txt'
        dest_path = os.path.join(os.path.dirname(__file__), 'test_data')
        resp, content = self.client.download_file(file_path,
                                                  dest_path=dest_path)
        written_file = os.path.join(dest_path, 'test_file1.txt')
        self.assertTrue(os.path.exists(written_file))
        file_fd = open(written_file, 'r')
        data = file_fd.read()
        file_fd.close
        os.remove(written_file)
        self.assertEqual(data, 'Test file\n')

    def test_chdir(self):
        """ test_chdir
        """
        path1 = ''
        path2 = '/'
        path3 = '/hello'
        path4 = 'hello/'

        self.client.connection.path = path1
        self.client.chdir('..')
        self.assertEqual(self.client.connection.path, '/')

        self.client.connection.path = path2
        self.client.chdir('..')
        self.assertEqual(self.client.connection.path, '/')

        self.client.connection.path = path3
        self.client.chdir('..')
        self.assertEqual(self.client.connection.path, '/')

        self.client.connection.path = path4
        self.client.chdir('..')
        self.assertEqual(self.client.connection.path, '/')

        self.client.connection.path = path1
        self.client.chdir('wibble')
        self.assertEqual(self.client.connection.path, '/wibble')

        self.client.chdir('wibble')
        self.assertEqual(self.client.connection.path, '/wibble/wibble')

        self.client.chdir('/foo/bar')
        self.assertEqual(self.client.connection.path, '/foo/bar')

    def test_ls(self):
        self.client.connection.path = 'webdav'
        self.client.connection.host = 'http://localhost:8008/'

        result = sorted(self.client.ls())

        expected_result = sorted([
            ['http://localhost:8008/webdav', 'httpd/unix-directory'],
            ['http://localhost:8008/webdav/newpath', 'httpd/unix-directory'],
            ['http://localhost:8008/webdav/test_dir1', 'httpd/unix-directory'],
            ['http://localhost:8008/webdav/test_file1.txt', 'text/plain'],
            ['http://localhost:8008/webdav/test_file2.txt', 'text/plain'],
            ['http://localhost:8008/webdav/test_file_post.txt', 'text/plain']])

        self.assertEqual(result[0][0:2], expected_result[0])
        self.assertEqual(result[1][0:2], expected_result[1])
        self.assertEqual(result[2][0:2], expected_result[2])
        self.assertEqual(result[3][0:2], expected_result[3])
        self.assertEqual(result[4][0:2], expected_result[4])
        self.assertEqual(result[5][0:2], expected_result[5])

        self.assertTrue(result[0][-1])
        self.assertTrue(result[1][-1])
        self.assertTrue(result[2][-1])
        self.assertTrue(result[3][-1])
        self.assertTrue(result[4][-1])
        self.assertTrue(result[5][-1])

    def test_ls_formats(self):
        self.client.connection.path = 'webdav'
        self.client.connection.host = 'http://localhost:8008/'

        result = sorted(
            self.client.ls(list_format=('C', 'F', 'A', 'E', 'D', 'T', 'M')))

        etag_regex = re.compile(r'(?i)([a-f0-9\-]+)')

        self.assertTrue(result[0][0] in ['text/plain', 'httpd/unix-directory'])
        self.assertTrue(result[0][1].startswith('http://localhost:8008/webdav'))
        self.assertTrue(result[0][2] in ['T', 'F', ''])
        self.assertTrue(etag_regex.match(result[0][3]))
        self.assertTrue(datetime.strptime(result[0][4], '%Y-%m-%dT%H:%M:%SZ'))
        self.assertTrue(result[0][5] in ['collection', 'resource'])
        self.assertTrue(datetime.strptime(result[0][6],
                                          '%a, %d %b %Y %H:%M:%S GMT'))
        self.assertTrue(result[1][0] in ['text/plain', 'httpd/unix-directory'])
        self.assertTrue(result[1][1].startswith('/webdav/'))
        self.assertTrue(result[1][2] in ['T', 'F', ''])
        self.assertTrue(etag_regex.match(result[1][3]))
        self.assertTrue(datetime.strptime(result[1][4], '%Y-%m-%dT%H:%M:%SZ'))
        self.assertTrue(result[1][5] in ['collection', 'resource'])
        self.assertTrue(datetime.strptime(result[1][6],
                                          '%a, %d %b %Y %H:%M:%S GMT'))
        self.assertTrue(result[2][0] in ['text/plain', 'httpd/unix-directory'])
        self.assertTrue(result[2][1].startswith('/webdav/'))
        self.assertTrue(result[2][2] in ['T', 'F', ''])
        self.assertTrue(etag_regex.match(result[2][3]))
        self.assertTrue(datetime.strptime(result[2][4], '%Y-%m-%dT%H:%M:%SZ'))
        self.assertTrue(result[2][5] in ['collection', 'resource'])
        self.assertTrue(datetime.strptime(result[2][6],
                                          '%a, %d %b %Y %H:%M:%S GMT'))
        self.assertTrue(result[3][0] in ['text/plain', 'httpd/unix-directory'])
        self.assertTrue(result[3][1].startswith('/webdav/'))
        self.assertTrue(result[3][2] in ['T', 'F', ''])
        self.assertTrue(etag_regex.match(result[3][3]))
        self.assertTrue(datetime.strptime(result[3][4], '%Y-%m-%dT%H:%M:%SZ'))
        self.assertTrue(result[3][5] in ['collection', 'resource'])
        self.assertTrue(datetime.strptime(result[3][6],
                                          '%a, %d %b %Y %H:%M:%S GMT'))
        self.assertTrue(result[4][0] in ['text/plain', 'httpd/unix-directory'])
        self.assertTrue(result[4][1].startswith('/webdav/'))
        self.assertTrue(result[4][2] in ['T', 'F', ''])
        self.assertTrue(etag_regex.match(result[4][3]))
        self.assertTrue(datetime.strptime(result[4][4], '%Y-%m-%dT%H:%M:%SZ'))
        self.assertTrue(result[4][5] in ['collection', 'resource'])
        self.assertTrue(datetime.strptime(result[4][6],
                                          '%a, %d %b %Y %H:%M:%S GMT'))
        self.assertTrue(result[5][0] in ['text/plain', 'httpd/unix-directory'])
        self.assertTrue(result[5][1].startswith('/webdav/'))
        self.assertTrue(result[5][2] in ['T', 'F', ''])
        self.assertTrue(etag_regex.match(result[5][3]))
        self.assertTrue(datetime.strptime(result[5][4], '%Y-%m-%dT%H:%M:%SZ'))
        self.assertTrue(result[5][5] in ['collection', 'resource'])
        self.assertTrue(datetime.strptime(result[5][6],
                                          '%a, %d %b %Y %H:%M:%S GMT'))

    def test_ls_no_format(self):
        self.client.connection.path = 'webdav'
        self.client.connection.host = 'http://localhost/'

        result = self.client.ls(list_format=tuple())
        self.assertEqual(result, [[], [], [], [], [], []])

    def test_mkdir(self):
        """ test_mkdir

            Test for making directories (collections)
        """
        self.client.connection.send_mkcol = mock.Mock()
        self.client.connection.path = 'myWebDAV'
        self.client.mkdir('newpath')
        self.assertEqual(self.client.connection.send_mkcol.call_args_list,
                          [(('myWebDAV/newpath',), {})])

    def test_rmdir(self):
        """ test_rmdir

            Test for removing directories
        """
        self.client.connection.send_rmcol = mock.Mock()
        self.client.connection.path = 'myWebDAV'
        self.client.rmdir('new_dir')
        self.assertEqual([(('myWebDAV/new_dir',), {})],
                          self.client.connection.send_rmcol.call_args_list)

    def test_pwd(self):
        """ test_pwd

            Test that the pwd method returns the current path stored in the
            connection object
        """
        self.client.connection.path = "/myWebDAV/monty"
        result = self.client.pwd()
        self.assertEqual(result, "/myWebDAV/monty")

    def test_pwd_none(self):
        """ test_pwd

            Test that the pwd method returns None when a connection has not been
            set up yet.
        """
        self.client.connection= None
        result = self.client.pwd()
        self.assertEqual(result, None)

    def test_upload_file_filename(self):
        """ Test that a file can be sent to a server
        """
        file_name = os.path.join(os.path.dirname(__file__), 'test_data',
                                 "some_file.txt")
        if not os.path.exists(file_name):
            open(file_name, 'wb').close()
        self.client.connection.send_put = mock.Mock()
        self.client.connection.send_put.return_value = (200, '')
        self.client.connection.path = 'myWebDAV'
        resp, cont = self.client.upload_file(file_name)
        os.remove(file_name)
        self.assertEqual(file_name,
                          self.client.connection.send_put.call_args[0][0])

    def test_upload_file_fileobj(self):
        """ Test that a file can be sent to a server
        """
        file_name = os.path.join(os.path.dirname(__file__), 'test_data',
                                 "some_file.txt")
        if not os.path.exists(file_name):
            open(file_name, 'wb').close()
        self.client.connection.send_put = mock.Mock()
        self.client.connection.send_put.return_value = (200, '')
        self.client.connection.path = 'myWebDAV'
        fd1 = open(file_name, 'r')
        try:
            resp, cont = self.client.upload_file(fd1)
        finally:
            if not fd1.closed:
                fd1.close()
                os.remove(file_name)
        self.assertEqual(file_name,
                          self.client.connection.send_put.call_args[0][0])