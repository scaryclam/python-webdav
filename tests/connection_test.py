""" These tests require a webdav server to be running in order to work
    correctly.

    PyWebDAV is a WebDAV server library that comes with a simple example
    server that allows simple usage. It is what this project uses to test
    against.
"""
import unittest
import os
#import httplib2
import socket
import mock
import requests
import shutil
import subprocess
import time
import python_webdav.connection

# Some WebDAV server settings.
LOCAL_DAV_DIR = "/tmp/"
DAV_ROOT_DIR = "webdav"
PORT = 8008
SERVER_CMD = "~/code/virtual/python-webdav/bin/davserver -D %s -n -P %d" % (LOCAL_DAV_DIR, PORT)

DIR_STRUCTURE = {DAV_ROOT_DIR: {'test_file1.txt': 'Test file',
                                'test_dir1': {}}}


def _create_files(dir_structure, dir_name=None):
    if not dir_name:
        dir_name = LOCAL_DAV_DIR
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    for key, val in dir_structure.iteritems():
        next_item = os.path.join(dir_name, key)
        try:
            val + ''
            with open(next_item, 'w') as item_fd:
                item_fd.write(val)
        except TypeError:
            # Is not a string
            _create_files(val, dir_name=next_item)


class TestConnection(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(LOCAL_DAV_DIR):
            os.mkdir(LOCAL_DAV_DIR)

        _create_files(DIR_STRUCTURE)

        # Start pywebdav server
        self.server_proc = subprocess.Popen(SERVER_CMD, shell=True)
        time.sleep(0.5)

        settings = dict(username='wibble',
                        password='fish',
                        realm='test-realm',
                        port=PORT,
                        host='http://webdav.example.com/webdav',
                        path='.')
        self.connection_obj = python_webdav.connection.Connection(settings)

    def tearDown(self):
        # Stop the server
        print "Stopping server"
        result = self.server_proc.kill()
        print result

        # Delete the directory structure
        shutil.rmtree(os.path.join(LOCAL_DAV_DIR, DAV_ROOT_DIR))

    def test_connection_settings(self):
        self.assertEquals(self.connection_obj.username, 'wibble')
        self.assertEquals(self.connection_obj.password, 'fish')
        self.assertEquals(self.connection_obj.realm, 'test-realm')
        self.assertEquals(self.connection_obj.port, PORT)
        self.assertEquals(self.connection_obj.host,
                          'http://webdav.example.com/webdav')
        self.assertEquals(self.connection_obj.path, '.')
        self.assertEquals(self.connection_obj.httpcon.auth, ('wibble', 'fish',))
        self.assertTrue(isinstance(self.connection_obj.httpcon,
                                   requests.Session))

    def test_send_request(self):
        self.connection_obj.host = 'http://localhost:%d/webdav' % PORT
        resp, content = self.connection_obj._send_request('GET', '')
        self.assertEquals(resp.status_code, 200)

    def test_send_get(self):
        self.connection_obj.host = 'http://localhost:%d/webdav' % PORT
        path = ''
        resp, content = self.connection_obj.send_get(path)
        self.assertEquals(resp.status_code, 200)

    def test_send_get_raises_error(self):
        path = 'cake'
        self.assertRaises(requests.ConnectionError,
                          self.connection_obj.send_get, path)

    def test_send_put(self):
        self.connection_obj.host = 'http://localhost:%d/webdav' % PORT
        path = '/webdav/test_file_post.txt'
        test_file = os.path.join(os.path.dirname(__file__),
                                 'test_data', 'test_file_post.txt')
        file_to_send = open(test_file, 'r')
        body = file_to_send.read()
        resp, content = self.connection_obj.send_put(path, body=body)
        self.assertTrue(resp.status_code in [201, 204])

    def test_send_put_raises(self):
        self.connection_obj.host = 'http://imnothere-haghashkddshkahdskhds.com'
        path = '/webdav/test_file_post.txt'
        body = ''
        self.assertRaises(requests.ConnectionError,
                          self.connection_obj.send_put, path, body=body)

    def test_send_delete(self):
        self.connection_obj.host = 'http://localhost:%d/webdav' % PORT
        path = '/webdav/test_file_post.txt'
        dir_path = os.path.join('/tmp', 'webdav', 'test_file_post.txt')
        if not os.path.exists(dir_path):
            open(dir_path, 'w').close()
        resp, content = self.connection_obj.send_delete(path)
        self.assertTrue(resp.status_code in [204])

    def test_send_delete_not_there(self):
        self.connection_obj.host = 'http://localhost:%d/webdav' % PORT
        path = '/webdav/imnothere'
        resp, content = self.connection_obj.send_delete(path)
        self.assertEquals(resp.status_code, 404)

    def test_send_delete_raises(self):
        self.connection_obj.host = 'http://imnothere-ahsadhashadshds.com'
        path = '/webdav/test_file_post.txt'
        self.assertRaises(requests.ConnectionError,
                          self.connection_obj.send_delete, path)

    def test_send_propget_root(self):
        self.connection_obj.host = 'http://localhost:%d/webdav' % PORT
        path = ''
        resp, content = self.connection_obj.send_propfind(path)

        expected_resp_status = 207
        expected_content = '<?xml version="1.0" encoding="utf-8"?>\n<D:multistatus xmlns:D="DAV:">'
        content_sample = '\n'.join(content.split('\n')[:2])

        self.assertEquals(expected_resp_status, resp.status_code)
        self.assertEquals(expected_content, content_sample)

    def test_send_propget_file(self):
        self.connection_obj.host = 'http://localhost:%d/webdav/test_file1.txt' % PORT
        path = ''
        resp, content = self.connection_obj.send_propfind(path)

        expected_resp_status = 207
        expected_content = '<?xml version="1.0" encoding="utf-8"?>\n<D:multistatus xmlns:D="DAV:">'
        content_sample = '\n'.join(content.split('\n')[:2])

        self.assertEquals(expected_resp_status, resp.status_code)
        self.assertEquals(expected_content, content_sample)

    def test_send_propget_path(self):
        self.connection_obj.host = 'http://localhost:%d/webdav' % PORT
        path = 'test_dir1/'
        dir_path = os.path.join('/tmp', 'webdav', 'test_dir1')
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        resp, content = self.connection_obj.send_propfind(path)

        expected_resp_status = 207
        expected_content = '<?xml version="1.0" encoding="utf-8"?>\n<D:multistatus xmlns:D="DAV:">'
        content_sample = '\n'.join(content.split('\n')[:2])

        self.assertEquals(expected_resp_status, resp.status_code)
        self.assertEquals(expected_content, content_sample)

    def test_send_propget_raises_error(self):
        self.connection_obj.host = 'http://nothereabsbdbabsbdabbabsdbashsjh.com'
        path = ''
        self.assertRaises(requests.ConnectionError,
                          self.connection_obj.send_propfind, path)

    def test_send_lock(self):
        self.connection_obj.host = 'http://localhost:%d/webdav' % PORT
        path = 'test_file1.txt'
        resp, content, lock = self.connection_obj.send_lock(path)
        lock_fd = open('tst_lock.txt', 'w')
        lock_fd.write(lock.token)
        lock_fd.close()
        self.assertEquals(200, resp.status_code)
        self.assertTrue(lock.token)

    def test_send_unlock(self):
        self.connection_obj.host = 'http://localhost:%d/webdav/test_file1.txt' % PORT
        path = ''
        lock_file = os.path.join(os.path.dirname(__file__), 'test_data',
                                 'tst_lock.txt')
        lock_fd = open(lock_file, 'r')
        token = lock_fd.read()
        lock_fd.close()
        os.remove(lock_file)
        lock_token = python_webdav.connection.LockToken(token)
        resp, content = self.connection_obj.send_unlock(path, lock_token)
        self.assertEquals(204, resp.status_code)

    def test_send_mkcol(self):
        self.connection_obj.host = 'http://localhost:%d/webdav' % PORT
        path = 'wibble/'
        resp, content = self.connection_obj.send_mkcol(path)
        self.assertEquals(201, resp.status_code)

    def test_send_rmcol(self):
        dir_path = os.path.join('/tmp', 'webdav', 'wibble')
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        self.connection_obj.host = 'http://localhost:%d/webdav' % PORT
        path = 'wibble/'
        resp, content = self.connection_obj.send_rmcol(path)
        self.assertEquals(204, resp.status_code)

    def test_send_copy_same_dir(self):
        self.connection_obj.host = 'http://localhost:%d/webdav' % PORT
        path = 'webdav/test_file1.txt'
        destination = 'webdav/temp_file_copy.txt'
        resp, content = self.connection_obj.send_copy(path, destination)
        self.connection_obj.send_delete(destination)
        self.assertTrue(resp.status_code in [201, 204])


class TestProperty(unittest.TestCase):
    def setUp(self):
        self.prop_obj = python_webdav.connection.Property()

    def set_property_test(self):
        self.prop_obj.set_property('wibble', 123)
        self.assertEquals(self.prop_obj.wibble, 123)


class TestClient(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(LOCAL_DAV_DIR):
            os.mkdir(LOCAL_DAV_DIR)

        _create_files(DIR_STRUCTURE)

        # Start pywebdav server
        self.server_proc = subprocess.Popen(SERVER_CMD, shell=True)
        time.sleep(0.5)

        self.client_obj = python_webdav.connection.Client()

    def tearDown(self):
        # Stop the server
        print "Stopping server"
        result = self.server_proc.kill()
        print result

        # Delete the directory structure
        shutil.rmtree(os.path.join(LOCAL_DAV_DIR, DAV_ROOT_DIR))

    def test_parse_xml_prop(self):
        xml = '''<?xml version="1.0" encoding="utf-8"?>
<D:multistatus xmlns:D="DAV:">
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://apache.org/dav/props/">
<D:href>/webdav/</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype><D:collection/></lp1:resourcetype>
<lp1:creationdate>2009-09-02T20:50:58Z</lp1:creationdate>
<lp1:getlastmodified>Wed, 02 Sep 2009 20:50:58 GMT</lp1:getlastmodified>
<lp1:getetag>"31411a-1000-4729e6c869080"</lp1:getetag>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
<D:getcontenttype>httpd/unix-directory</D:getcontenttype>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://apache.org/dav/props/">
<D:href>/webdav/foobag.txt</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2009-09-02T20:31:52Z</lp1:creationdate>
<lp1:getcontentlength>7</lp1:getcontentlength>
<lp1:getlastmodified>Wed, 02 Sep 2009 20:31:52 GMT</lp1:getlastmodified>
<lp1:getetag>"314189-7-4729e2837fe00"</lp1:getetag>
<lp2:executable>F</lp2:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
<D:getcontenttype>text/plain</D:getcontenttype>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://apache.org/dav/props/">
<D:href>/webdav/cake/</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype><D:collection/></lp1:resourcetype>
<lp1:creationdate>2009-09-02T20:50:58Z</lp1:creationdate>
<lp1:getlastmodified>Wed, 02 Sep 2009 20:50:58 GMT</lp1:getlastmodified>
<lp1:getetag>"314188-1000-4729e6c869080"</lp1:getetag>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
<D:getcontenttype>httpd/unix-directory</D:getcontenttype>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
</D:multistatus>'''
        #properties = self.client_obj.parse_xml_prop(xml)
        import python_webdav.parse
        #parser = python_webdav.parse.LxmlParser()
        parser = python_webdav.parse.SoupParser()
        properties = parser.parse(xml)
        ##properties = parser.response_objects
        self.assertEquals(len(properties), 3)
        self.assertEquals(sorted(properties[0].__dict__),
                          sorted({'getetag': u'"31411a-1000-4729e6c869080"',
                                  'status': u'HTTP/1.1 200 OK',
                                  'getlastmodified': u'Wed, 02 Sep 2009 20:50:58 GMT',
                                  'resourcetype': u'collection',
                                  'href': u'/webdav/',
                                  'getcontenttype': u'httpd/unix-directory',
                                  'locks': [],
                                  'executable': None,
                                  'getcontentlength': None,
                                  'creationdate': u'2009-09-02T20:50:58Z'}))
        self.assertEquals(sorted(properties[1].__dict__),
                          sorted({'getetag': u'"314189-7-4729e2837fe00"',
                                  'status': u'HTTP/1.1 200 OK',
                                  'getlastmodified': u'Wed, 02 Sep 2009 20:31:52 GMT',
                                  'resourcetype': 'resource',
                                  'href': u'/webdav/foobag.txt',
                                  'getcontenttype': u'text/plain',
                                  'locks': [],
                                  'executable': u'F',
                                  'getcontentlength': u'7',
                                  'creationdate': u'2009-09-02T20:31:52Z'}))
        self.assertEquals(sorted(properties[2].__dict__),
                          sorted({'getetag': u'"314188-1000-4729e6c869080"',
                                  'status': u'HTTP/1.1 200 OK',
                                  'getlastmodified': u'Wed, 02 Sep 2009 20:50:58 GMT',
                                  'resourcetype': u'collection',
                                  'href': u'/webdav/cake/',
                                  'getcontenttype': u'httpd/unix-directory',
                                  'locks': [],
                                  'executable': None,
                                  'getcontentlength': None,
                                  'creationdate': u'2009-09-02T20:50:58Z'}))

    def test_get_properties(self):
        settings = dict(username='wibble',
                        password='fish',
                        realm='test-realm',
                        port=PORT,
                        host='http://localhost:%d/webdav' % PORT,
                        path='webdav')
        connection_obj = python_webdav.connection.Connection(settings)

        client = python_webdav.connection.Client()
        client.get_properties = mock.Mock()
        mock_prop1 = MockProperty()
        mock_prop1.john = 'cleese'
        mock_prop1.eric = 'idle'
        mock_prop1.graham = 'chapman'
        mock_prop1.terry = 'gilliam'
        mock_prop1.Terry = 'jones'
        mock_prop1.michael = 'palin'

        client.get_properties.return_value = [mock_prop1]
        properties = ['john', 'eric', 'graham', 'terry', 'Terry', 'michael']
        result_properties = client.get_properties(connection_obj,
                                                  'webdav/test_file1.txt',
                                                  properties=properties)
        result = result_properties[-1]
        self.assertEquals(result.terry, 'gilliam')
        self.assertEquals(result.michael, 'palin')
        self.assertEquals(result.Terry, 'jones')
        self.assertEquals(result.john, 'cleese')
        self.assertEquals(result.graham, 'chapman')
        self.assertEquals(result.eric, 'idle')

    def test_get_property(self):
        settings = dict(username='wibble',
                        password='fish',
                        realm='test-realm',
                        port=PORT,
                        host='http://localhost:%d/webdav' % PORT,
                        path='webdav')
        connection_obj = python_webdav.connection.Connection(settings)
        client = python_webdav.connection.Client()
        client.get_properties = mock.Mock()
        mock_prop = MockProperty()
        mock_prop.parrot = 'dead'
        client.get_properties.return_value = [mock_prop]
        property_name = 'parrot'
        requested_value = client.get_property(connection_obj,
                                              'webdav/test_file1.txt',
                                              property_name)
        self.assertEquals(requested_value, 'dead')

    def test_get_file(self):
        settings = dict(username='wibble',
                        password='fish',
                        realm='test-realm',
                        port=PORT,
                        host='http://localhost:%d/webdav' % PORT,
                        path='webdav')
        connection_obj = python_webdav.connection.Connection(settings)

        connection_obj.send_get = mock.Mock()
        mock_resp = MockProperty()
        mock_resp.status_code = 204
        connection_obj.send_get.return_value = (mock_resp, 'Data')
        client = python_webdav.connection.Client()
        requested_value = client.get_file(connection_obj,
                                          'webdav/test_file1.txt',
                                          'local_file.txt')
        self.assertTrue(os.path.exists('local_file.txt'))
        self.assertTrue(os.path.getsize('local_file.txt') > 0)
        file_fd = open('local_file.txt', 'r')
        file_data = file_fd.read()
        file_fd.close()
        os.remove('local_file.txt')
        self.assertEquals(file_data, 'Data')

    def test_send_file(self):
        settings = dict(username='wibble',
                        password='fish',
                        realm='test-realm',
                        port=PORT,
                        host='http://localhost:%d/webdav' % PORT,
                        path='webdav')
        connection_obj = python_webdav.connection.Connection(settings)
        connection_obj.send_put = mock.Mock()
        mock_resp = MockProperty()
        mock_resp.status_code = 204
        connection_obj.send_put.return_value = (mock_resp, '')
        client = python_webdav.connection.Client()
        local_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                  'test_data', 'test_file_post.txt')
        resp, contents = client.send_file(connection_obj,
                                          'webdav/test_file_post.txt',
                                          local_file)
        self.assertEquals(resp.status_code, 204)

    def test_copy_resource(self):
        settings = dict(username='wibble',
                        password='fish',
                        realm='test-realm',
                        port=PORT,
                        host='http://localhost:%d/webdav' % PORT,
                        path='webdav')
        connection_obj = python_webdav.connection.Connection(settings)
        connection_obj.send_copy = mock.Mock()
        mock_resp = MockProperty()
        mock_resp.status_code = 204
        connection_obj.send_copy.return_value = (mock_resp, '')
        client = python_webdav.connection.Client()
        resource_uri = 'webdav/test_file1.txt'
        resource_destination = 'webdav/test_file1_copy.txt'
        resp, contents = client.copy_resource(connection_obj, resource_uri,
                                              resource_destination)
        self.assertTrue(resp.status_code > 200)

    def test_delete_resource(self):
        settings = dict(username='wibble',
                        password='fish',
                        realm='test-realm',
                        port=PORT,
                        host='http://localhost:%d/webdav' % PORT,
                        path='webdav')
        connection_obj = python_webdav.connection.Connection(settings)
        connection_obj.send_delete = mock.Mock()
        mock_resp = MockProperty()
        mock_resp.status_code = 204
        connection_obj.send_delete.return_value = (mock_resp, '')
        client = python_webdav.connection.Client()
        resource_uri = 'webdav/test_file1_copy.txt'
        resp, contents = client.delete_resource(connection_obj, resource_uri)
        self.assertTrue(resp.status_code > 200)

    def test_lock(self):
        settings = dict(username='wibble',
                        password='fish',
                        realm='test-realm',
                        port=PORT,
                        host='http://localhost:%d/webdav' % PORT,
                        path='webdav')
        connection_obj = python_webdav.connection.Connection(settings)
        connection_obj.send_lock = mock.Mock()
        connection_obj.send_lock.return_value = "lock string"
        client = python_webdav.connection.Client()
        resource_uri = 'webdav/test_file1_copy.txt'
        result = client.get_lock(resource_uri, connection_obj)
        self.assertEquals(result, "lock string")
        self.assertEquals(connection_obj.locks[resource_uri].token, "lock string")

    def test_lock_raises_no_server(self):
        settings = dict(username='wibble',
                        password='fish',
                        realm='test-realm',
                        port=PORT,
                        host='http://examplgregrerge.net/foo',
                        path='webdav')
        connection_obj = python_webdav.connection.Connection(settings)
        #connection_obj.send_lock = mock.Mock()
        #connection_obj.send_lock.return_value = "lock string"
        client = python_webdav.connection.Client()
        resource_uri = 'webdav/test_file1_copy.txt'
        self.assertRaises(requests.ConnectionError, client.get_lock,
                          resource_uri, connection_obj)

    def test_unlock(self):
        settings = dict(username='wibble',
                        password='fish',
                        realm='test-realm',
                        port=PORT,
                        host='http://localhost:%d/webdav' % PORT,
                        path='webdav')
        connection_obj = python_webdav.connection.Connection(settings)
        connection_obj.send_unlock = mock.Mock()
        connection_obj.send_unlock.return_value = 200, "OK"
        client = python_webdav.connection.Client()
        resource_uri = 'webdav/test_file1_copy.txt'
        connection_obj.locks[resource_uri] = 'thisisalock'
        result = client.release_lock(resource_uri, connection_obj)
        self.assertFalse(connection_obj.locks.get(resource_uri))
        self.assertEquals(result, 200)

    def test_unlock_raises_no_server(self):
        settings = dict(username='wibble',
                        password='fish',
                        realm='test-realm',
                        port=PORT,
                        host='http://www.exampleNOTHERE.net',
                        path='webdav')
        connection_obj = python_webdav.connection.Connection(settings)
        #connection_obj.send_unlock = mock.Mock()
        #connection_obj.send_unlock.return_value = 200, "OK"
        client = python_webdav.connection.Client()
        resource_uri = 'webdav/test_file1_copy.txt'
        tocken = python_webdav.connection.LockToken('thisisalock')
        connection_obj.locks[resource_uri] = tocken
        self.assertRaises(requests.ConnectionError,
                          client.release_lock, resource_uri, connection_obj)

    def test_unlock_returns_false(self):
        settings = dict(username='wibble',
                        password='fish',
                        realm='test-realm',
                        port=PORT,
                        host='http://localhost:%d/webdav' % PORT,
                        path='webdav')
        connection_obj = python_webdav.connection.Connection(settings)
        connection_obj.send_unlock = mock.Mock()
        connection_obj.send_unlock.return_value = 200, "OK"
        client = python_webdav.connection.Client()
        resource_uri = 'webdav/test_file1_copy.txt'
        result = client.release_lock(resource_uri, connection_obj)
        self.assertFalse(connection_obj.locks.get(resource_uri))
        self.assertEquals(result, False)

#def test_lock(self):
    #connection_obj = python_webdav.connection.Connection(settings)
    #connection_obj.send_lock = mock.Mock()
    #connection_obj.send_lock.return_value = "lock string"
    #client = python_webdav.connection.Client()
    #resource_uri = 'webdav/test_file1_copy.txt'
    #result = client.get_lock(resource_uri
    #assert result == "lock string"
    #assert client.locks == {resource_uri: "lock string"}
    #assert 1 == 2


class MockProperty(object):
    def __init__(self):
        pass


if __name__ == '__main__':
    print "*** Finished Tests ***"