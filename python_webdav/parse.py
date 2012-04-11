""" parse.py
    Module for some of the webdav response parsing requirements
"""
from lxml.etree import ElementTree, HTML


class Response(object):
    """ Response objects are for storing information about resources
    """

    def __init__(self):
        """ Response objects are for storing information about resources
        """
        self.href = None
        self.resourcetype = None
        self.creationdate = None
        self.getcontentlength = None
        self.getlastmodified = None
        self.getetag = None
        self.executable = None
        self.locks = []
        self.getcontenttype = None
        self.status = None


class Lock(object):
    """ This is an object for storing resource lock information
    """
    def __init__(self):
        """ There are no inputs for this object but self.locktype and
            self.lockscope will be initialised to None when the instance is
            created
        """
        self.locktype = None
        self.lockscope = None


class LxmlParser(object):
    """ Parser for the Webdav replies
    """
    def __init__(self):
        """ No inputs

        """
        self.element_list = []
        self.closed_elements = []
        self.response_objects = []
        self.current_element = None
        self.is_lock = False

    def parse(self, data):
        """ Parse a webdav reply. Retrieve any resources as objects
            and return them as a list.

            :param data: The webdav reply to parse
            :type data: String


            :return: self.response_objects

        """
        data_elements = HTML(data)
        xml_etree = ElementTree(data_elements)
        all_response_elements = xml_etree.findall("//response")
        for response in all_response_elements:
            new_response = Response()
            resp_tree = ElementTree(response)
            new_response.href = resp_tree.find('//href').text
            if resp_tree.find('//collection') is not None:
                new_response.resourcetype = 'collection'
            else:
                new_response.resourcetype = 'resource'
                new_response.executable = getattr(
                    resp_tree.find('//executable'), 'text', None)
            new_response.creationdate = getattr(
                resp_tree.find('//creationdate'), 'text', None)
            new_response.getcontentlength = getattr(
                resp_tree.find('//getcontentlength'), 'text', None)
            new_response.getlastmodified = getattr(
                resp_tree.find('//getlastmodified'), 'text', None)
            new_response.getetag = getattr(
                resp_tree.find('//getetag'), 'text', None)
            new_response.getcontenttype = getattr(
                resp_tree.find('//getcontenttype'), 'text', None)
            new_response.status = getattr(
                resp_tree.find('//status'), 'text', None)

            # Now we have the properties that are easy to get,
            # lets get the lock information
            lock_tree = resp_tree.findall('//lockentry')
            for lock in lock_tree:
                lock_tree = ElementTree(lock)
                lock_obj = Lock()
                lock_obj.locktype = lock_tree.find(
                    '//locktype').getchildren()[-1].tag
                lock_obj.lockscope = lock_tree.find(
                    '//lockscope').getchildren()[-1].tag
                new_response.locks.append(lock_obj)

            self.response_objects.append(new_response)

        return self.response_objects
