import python_webdav
import python_webdav.client
import optparse
import sys
import urllib2

#class PythonWebdavClient(object):
    #def __init__(self, server=None):
        #if server:
            #host, path = urllib2.splithost(urllib2.splittype(server)[-1])
            #if not path:
                #path = '/'
            #self.conn = python_webdav.client.Client(server, webdav_path=path)
            #self.conn.set_connection('wibble', 'fish')
        #else:
            #print "I need a server!"
            #self.conn = None

class Client(object):
    def __init__(self):
        pass

    def main(self, argv):
        parser = optparse.OptionParser()
        opts, args = parser.parse_args(argv)
        if len(args) > 1:
            server = args[1]
            print "Server:", server
        else:
            server = None
        self._setup_server(server=server)

        while 1:
            var = raw_input("python-webdav:%s$ " %
                            self.client_con.pwd()).split(' ')
            command = var[0]
            if len(var) > 1:
                wd_argv = var[1:]
            else:
                wd_argv = []
            wd_parser = optparse.OptionParser()
            wd_opts, wd_args = wd_parser.parse_args(wd_argv)
            if command == 'q':
                break
            elif command == 'ls':
                self.list()
            elif command == 'cd':
                next_path = wd_args[0]
                if next_path[-1] != '/':
                    next_path += '/'
                self.cd(next_path)
            else:
                print "Command Not Found\n"

    def cd(self, next_path):
        self.client_con.chdir(next_path)

    def list(self):

        listings = self.client_con.ls(self.client_con.pwd(),
                                           display=False)
        for listing in listings:
            print '\t\t'.join([item for item in listing])

    def _setup_server(self, server=None):
        if server:
            host, path = urllib2.splithost(urllib2.splittype(server)[-1])
            if not path:
                path = '/'
            self.client_con = python_webdav.client.Client(host,
                                                          webdav_path=path)
            self.client_con.set_connection('wibble', 'fish')
        else:
            print "I need a server!"
            self.client_con = None


if __name__ == '__main__':
    start = Client()
    try:
        start.main(sys.argv)
    except EOFError, err:
        print ''
    print "Exiting"