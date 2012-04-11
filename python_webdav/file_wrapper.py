""" filewrapper.py
    This file contains a FileWrapper object, the purpose of which is to
    provide a file like object that can be used with httplib2.

    This is currently required because httplib2 does not allow easy use of
    normal file objects. It will consume a file object on the first attempt
    at sending to a server. If the server requires authentication the file
    object is then not in a state to be used again, causing problems.
    This object also helps to get around the problem of getting progress
    back from httplib2 and httplib. It is possible to provide a callback
    function and a callback size.
"""
import os

class FileWrapper(file):
    """ This is currently required because httplib2 does not allow easy use of
        normal file objects. It will consume a file object on the first attempt
        at sending to a server. If the server requires authentication the file
        object is then not in a state to be used again, causing problems.
        This object also helps to get around the problem of getting progress
        back from httplib2 and httplib. It is possible to provide a callback
        function and a callback size.

        :param force_size: Sets a size to force the file to be read
                           in this sized blocks. httplib will send files
                           in 8192 chunks if force_size is not set.
        :type force_size: int

        :param callback: function to call when a percentage step is reached
        :type callback: function

        :param callback_size: Step (in percentage) at which callback should
                              be called. This must be larger than 0.
        :type callback_size: int
    """
    def __init__(self, name, mode=None, buffering=-1, force_size=False,
                 callback=None, callback_size=100):
        super(FileWrapper, self).__init__(name, mode=mode,
                                          buffering=buffering)
        #file.__init__(self, name, mode=mode, buffering=buffering)

        # Get options
        self.force_size = force_size
        self.callback = callback
        self.callback_percent = callback_size

        # Avoid Zero division errors
        if self.callback_percent == 0:
            self.callback_percent = 1

        # This next line may be redundant
        self.initial_read_pos = self.tell()
        self.file_size = os.path.getsize(self.name)

    def read(self, size=-1):
        """ Just like a file objects read method but will "rewind" after the
            file has reached EOF.
        """
        if self.force_size:
            size = self.force_size
        data = file.read(self, size)

        if not data or size < 0 or size >= self.file_size:
            self.seek(self.initial_read_pos)

        try:
            if size == -1:
                size = len(data)
            percent = int((float(size) / self.file_size) * 100)
        except ZeroDivisionError:
            percent = 0

        if self.callback and percent % self.callback_percent == 0:
            self.callback(percent)

        return data
