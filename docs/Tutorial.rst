========
Tutorial
========

------------
Introduction
------------

The idea behind the python-webdav library is to provide developers with an easy to use library that can also allow for a finer grain of control when needed.

The library currently contains two main modules: connection and client

Connection Module
*****************

The connection module itself has four classes: Connection, Client, LockToken and Property.

Connection
''''''''''

The Connection class is for setting up a connection object and using it to send HTTP requests to a WebDAV server.

It is a low level class that is meant for direct communication with the server. This can be used for programs that have a need control over the connection.

.. note: It currently uses httplib2. However, as WebDAV is used for file transfer, among other things, it may be neccessary to use httplib instead as it allows the sending of files by reading parts of the file at a time, rather than requireing all data to be sent to be sent at once.

Client
''''''

The Client class contains methods for getting and parsing WebDAV responses. It is mainly for use as a sort of abstraction from the Connection class.


LockToken
'''''''''

Lock tokens are used to aid in basic access control for files contained on a WebDAV server. This is a simple class for containing a lock token as an object.


Property
''''''''

Properties are objects used to store information about Resources properties.


First basic examples
********************

To import the library, use:

.. code-block:: python

  import python_webdav

Using the basic functionality of the library is simple. Start by making a Client object:

.. code-block:: python

  import python_webdav.client as pywebdav_client

  client_object = pywebdav_client.Client('https://webdav.example.net/')
  client_object.set_connection(username='KingArthur', password='HolyGrail')

This will set up a Client object that will communicate with the given server and credentials.

The idea of setting up the server and authentication information seperately, is to allow the connection to be used for different users, instead of havingto create individual connections for each user.

To download a file:

.. code-block:: python

  import python_webdav

  client_object = python_webdav.Client('https://webdav.example.net/')
  client_object.set_connection(username='KingArthur', password='HolyGrail')

  client_object.download_file('some_file.txt', dest_path='.')

More example code
*****************

More complete examples can be found in the docs/examples directory.
