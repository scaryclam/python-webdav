python_webdav
=============

python_webdav is a client side library, written in Python for WebDAV.

The library has been updated to use requests rather tha httplib2 for making the webdav calls.
The overall API has not been changed so there should not be any need to update current code bases.

INSTALLATION
------------

Install using:

  python setup.py install

or just install using pip:

  pip install python_webdav


CONTRIBUTING
------------

Contributions and improvements are always welcome. Contributions that do not adhere to PEP8
(where sensible) or do not have unit tests will unfortunately be turned down (clean and tested code
is happy code :)


TEST SUITE
----------

Things you might like to know about the test suite:

 # It's a pain to run some of the tests.

 Ok, I'm sorry, a lot of the tests are not actually unit tests. At some point I would love
 to get a nice, contained environment that I can put out there with the test suite so that
 real tests can be run against a temporary server. Right now I'm using the pywebdav server
 to run the tests against.
 If you want to write real unit tests then that's fine. I've avoided it purely because I'm
 not a webdav server expert and didn't trust my test data to be accurate.

