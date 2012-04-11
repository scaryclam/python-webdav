import unittest
import os
import python_webdav.file_wrapper as fw

class FileWrapperTest(unittest.TestCase):
    def setUp(self):
        if os.path.exists("thing.txt"):
            os.remove("thing.txt")
        fd1 = fw.FileWrapper("thing.txt", "w")
        fd1.write("Hello World!")
        fd1.close()

    def tearDown(self):
        if os.path.exists("thing.txt"):
            os.remove("thing.txt")

    def test_reads_full_file(self):

        self.assertTrue(os.path.exists("thing.txt"))

        fd2 = fw.FileWrapper("thing.txt", "r")
        data1 = fd2.read()
        tell_pos1 = fd2.tell()
        fd2.close()

        self.assertEquals(data1, "Hello World!")
        self.assertEquals(tell_pos1, 0)

    def test_reads_two_parts(self):
        self.assertTrue(os.path.exists("thing.txt"))
        fd3 = fw.FileWrapper("thing.txt", "r")
        data_first = fd3.read(5)
        tell_pos1 = fd3.tell()
        data_second = fd3.read(7)
        tell_pos2 = fd3.tell()

        fd3.close()

        self.assertEquals(data_first, 'Hello')
        self.assertEquals(data_second, " World!")
        self.assertEquals(tell_pos1, 5)
        self.assertEquals(tell_pos2, 12)

    def test_read_parts_plus_1(self):
        self.assertTrue(os.path.exists("thing.txt"))
        fd3 = fw.FileWrapper("thing.txt", "r")
        data_first = fd3.read(5)
        tell_pos1 = fd3.tell()
        data_second = fd3.read(7)
        tell_pos2 = fd3.tell()

        data_third = fd3.read(1)
        tell_pos3 = fd3.tell()

        fd3.close()

        self.assertEquals(data_first, 'Hello')
        self.assertEquals(data_second, " World!")
        self.assertEquals(data_third, "")
        self.assertEquals(tell_pos1, 5)
        self.assertEquals(tell_pos2, 12)
        self.assertEquals(tell_pos3, 0)


    def test_read_beyond(self):
        self.assertTrue(os.path.exists("thing.txt"))
        fd3 = fw.FileWrapper("thing.txt", "r")
        data_first = fd3.read()
        tell_pos1 = fd3.tell()
        data_second = fd3.read(7)
        tell_pos2 = fd3.tell()

        fd3.close()

        self.assertEquals(data_first, 'Hello World!')
        self.assertEquals(data_second, "Hello W")
        self.assertEquals(tell_pos1, 0)
        self.assertEquals(tell_pos2, 7)

    def test_read_too_much(self):
        self.assertTrue(os.path.exists("thing.txt"))
        fd3 = fw.FileWrapper("thing.txt", "r")
        data_first = fd3.read(100)
        tell_pos1 = fd3.tell()

        fd3.close()

        self.assertEquals(data_first, 'Hello World!')
        self.assertEquals(tell_pos1, 0)

    def read_start_then_rest(self):
        self.assertTrue(os.path.exists("thing.txt"))
        fd3 = fw.FileWrapper("thing.txt", "r")
        data_first = fd3.read(5)
        tell_pos1 = fd3.tell()
        data_second = fd3.read()
        tell_pos2 = fd3.tell()

        fd3.close()

        self.assertEquals(data_first, 'Hello')
        self.assertEquals(data_second, " World!")
        self.assertEquals(tell_pos1, 0)
        self.assertEquals(tell_pos2, 0)

    def test_read_force_size(self):
        self.assertTrue(os.path.exists("thing.txt"))
        fd3 = fw.FileWrapper("thing.txt", "r", force_size=2)
        data1 = fd3.read(1)
        data2 = fd3.read(2)
        data3 = fd3.read(3)
        data4 = fd3.read()

        fd3.close()

        self.assertEquals(data1, 'He')
        self.assertEquals(data2, 'll')
        self.assertEquals(data3, 'o ')
        self.assertEquals(data4, 'Wo')

    def test_callback_runs_default_percent(self):
        test_callback_obj = DummyObj()

        self.assertTrue(os.path.exists("thing.txt"))
        fd3 = fw.FileWrapper("thing.txt", "r",
                             callback=test_callback_obj.dummy_callback)
        fd3.read()
        fd3.close()
        self.assertEqual(test_callback_obj.percent, 100)

    def test_callback_runs_ten_percent(self):
        test_callback_obj = DummyObj()

        fd4 = fw.FileWrapper('thing.txt', 'r',
                             callback=test_callback_obj.dummy_callback,
                             callback_size=10)
        fd4.read()
        fd4.close()
        self.assertEqual(test_callback_obj.percent, 100)

    def test_callback_runs_twenty_percent(self):
        """ Callbacks are made every 20 percent
        """
        test_callback_obj = DummyObj(cb_percent=20)

        fd4 = fw.FileWrapper('thing.txt', 'r',
                             callback=test_callback_obj.dummy_callback,
                             callback_size=20)
        fd4.read()
        fd4.close()
        self.assertEqual(test_callback_obj.percent, 100)

    def test_callback_runs_twenty_percent_small(self):
        """ Callbacks are made every 20 percent but keep the dummy object
            at 10 so we can check it does not underrun
        """
        test_callback_obj = DummyObj()

        fd4 = fw.FileWrapper('thing.txt', 'r',
                             callback=test_callback_obj.dummy_callback,
                             callback_size=20)
        fd4.read()
        fd4.close()
        self.assertEqual(test_callback_obj.percent, 100)


class DummyObj(object):
    def __init__(self, cb_percent=10):
        self.percent = 0
        self.cb_percent = 10

    def dummy_callback(self, percent):
        self.percent = percent
