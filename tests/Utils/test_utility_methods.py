import os
from unittest import TestCase
from unittest.mock import mock_open, patch

from pydatpiff.utils.filehandler import File
from pydatpiff.utils.utils import Object, Select
from tests.utils import tmp_wrapper


class TestObjectMethods(TestCase):
    # pydatpiff.utils.utils.Object

    def test_object_is_dict_method_return_correct_type(self):
        self.assertTrue(Object.is_dict({"a": 1}))
        self.assertFalse(Object.is_dict(["a", "b"]))

    def test_object_is_string_method_return_correct_type(self):
        self.assertTrue(Object.is_string("a"))
        self.assertFalse(Object.is_string(["a", "b"]))

    def test_object_is_list_method_return_correct_type(self):
        self.assertTrue(Object.is_list(["a", "b"]))
        self.assertFalse(Object.is_list({"a": 1}))

    def test_object_strip_and_lower_method_return_correct_value(self):
        self.assertEqual(Object.strip_and_lower("a"), "a")
        self.assertEqual(Object.strip_and_lower(" a "), "a")
        self.assertEqual(Object.strip_and_lower(" A B "), "a b")

    def test_object_enumerate_option_returns_correct_value(self):
        self.assertEqual(Object.enumerate_options(["a", "b"]), [(0, "a"), (1, "b")])
        self.assertEqual(Object.enumerate_options({"a": 1, "b": 2}), [(0, ("a", 1)), (1, ("b", 2))])

        with self.assertRaises(NotImplementedError):
            Object.enumerate_options("a")


class TestSelect(TestCase):
    # pydatpiff.utils.utils.Select
    def test_select_by_choices_method_return_correct_value(self):
        self.assertEqual(Select.by_choices("a", ["a", "b"]), "a")
        self.assertEqual(Select.by_choices("a", ["a", "b"], fallback="c"), "a")
        self.assertEqual(Select.by_choices("c", ["a", "b"], fallback="b"), "b")
        self.assertEqual(Select.by_choices("a", {"a": "a", "b": "b"}), "a")
        self.assertEqual(Select.by_choices("a", {"a": "a", "b": "b"}, fallback="c"), "a")
        self.assertEqual(Select.by_choices("c", {"a": "a", "b": "b"}, fallback="b"), "b")

    def test_select_by_choices_method_raise_value_error(self):
        with self.assertRaises(ValueError):
            Select.by_choices("c", ["a", "b"], fallback=None)

        with self.assertRaises(ValueError):
            Select.by_choices("c", ["a", "b"], fallback="z")

        with self.assertRaises(ValueError):
            Select.by_choices("c", {"a": "a", "b": "b"}, fallback=None)

        with self.assertRaises(ValueError):
            Select.by_choices("c", {"a": "a", "b": "b"}, fallback="z")

    def test_get_leftmost_index_method_return_correct_value(self):
        self.assertEqual(Select.get_leftmost_index(1, ["a", "b"]), 0)
        self.assertEqual(Select.get_leftmost_index(2, ["a", "b"]), 1)
        self.assertEqual(Select.get_leftmost_index(1, {"a": "a", "b": "b"}), 0)
        self.assertEqual(Select.get_leftmost_index(2, {"a": "a", "b": "b"}), 1)

    def test_get_index_of_method_returns_correct_value(self):
        self.assertEqual(Select.get_index_of("a", ["a", "b"]), 0)
        self.assertEqual(Select.get_index_of("app", ["program", "application"]), 1)
        self.assertEqual(Select.get_index_of("a", {"a": "a", "b": "b"}), 0)
        self.assertEqual(Select.get_index_of("orange", {"apple": "apple", "orange": "peel"}), 1)


class TestFileClass(TestCase):
    @tmp_wrapper
    def test_file_is_dir_return_whether_path_is_dir(self, temp_file=None):
        dir_name = os.path.dirname(temp_file)
        self.assertTrue(File.is_dir(dir_name))

    @tmp_wrapper
    def test_file_is_file_return_whether_path_is_file(self, temp_file=None):
        self.assertTrue(File.is_file(temp_file))

    def test_file_join_join_path_correctly(self, temp_file=None):
        work_dir = os.getcwd()
        file_name = "some-mp3-file"
        expected = os.path.join(work_dir, file_name)
        self.assertEqual(File.join(to=file_name), expected)

        not_expected = "some-random-dir/" + file_name
        self.assertNotEqual(File.join(path=work_dir, to=file_name), not_expected)
        self.assertEqual(File.join(path="work_dir", to=file_name), expected)

    def test_file_standardize_file_name_correctly(self):
        self.assertEqual(File.standardize_file_name("(#*^some-file"), "some-file")
        unwanted_charaters = '!@#$%^&*()+{}|:"<>?`~'
        for char in unwanted_charaters:
            self.assertEqual(File.standardize_file_name(f"({char}some-file.mp3"), "some-file.mp3")

    @patch("builtins.open", new_callable=mock_open, read_data=b"some-mp3-content")
    def test_write_to_file_write_mp3_content_to_file_correctly(self, mocked_file):
        file_name = "some-file.mp3"
        file_content = b"some-mp3-content"

        File.write_to_file(filename=file_name, content=file_content)
        with open(file_name, "rb") as f:
            self.assertEqual(f.read(), file_content)

    def test_file_human_readable_file_size_return_correct_size(self):
        self.assertEqual(File.get_human_readable_file_size(1), "1B")
        self.assertEqual(File.get_human_readable_file_size(255), "255B")
        self.assertEqual(File.get_human_readable_file_size(2555), "2.5KB")
