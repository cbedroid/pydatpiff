import os
import re
import math
import sys
import unittest
from unittest.mock import Mock, patch, PropertyMock
from ...errors import AlbumError
from ...backend import filehandler


class TestFileSize(unittest.TestCase):
    def test_file_size_return_correct_size_name(self):
        file_size = filehandler.file_size
        byteCode = lambda value: re.sub(r"[\W\d]*", "", file_size(value))

        code_name = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
        buffer_size = 1

        # test file_size returns size over 0B
        # loop through all bytesCode while increasing buffersize by power of 1024
        for count, code in enumerate(code_name, start=0):
            buffer_size = math.pow(1024, count)
            self.assertEqual(code, byteCode(buffer_size))

        # test file_size return 0B when 0 pass to function
        self.assertEqual("0B", file_size(0))


class TestTMP(unittest.TestCase):
    def setUp(self):
        # patch module tempfile
        self.tempfile = patch.object(filehandler, "tempfile", autospec=True)
        self.MOCK_TMP = self.tempfile.start()
        self.addCleanup(patch.stopall)

        # TMP class
        self.TMP = filehandler.Tmp

    def test_tempfile_is_mock_correctly(self):
        self.assertTrue(filehandler.tempfile is self.MOCK_TMP)

    def test_create_tempfile_NameTemporaryFile(self):
        named_temp_file = self.MOCK_TMP.NamedTemporaryFile
        named_temp_file.return_value = "test_datpiff"
        tmp = self.TMP
        tmp.create()

        # test tempfile.NameTemporaryFile has suffix '_datiff'
        named_temp_file.assert_called_once_with(suffix="_datpiff", delete=False)

        # test tempfile.NameTemporaryFile return correct value
        self.assertEqual(named_temp_file.return_value, "test_datpiff")

    def test_Path_standardizing_path(self):
        path = "$$hello&&world"
        self.assertNotIn("$", filehandler.Path.standardizeName(path))
