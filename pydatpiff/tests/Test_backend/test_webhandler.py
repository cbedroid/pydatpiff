import os
import sys
import unittest
from unittest.mock import Mock, patch, PropertyMock
from ...backend import mediasetup, webhandler
from ...utils import request
from ..test_utils import mockSessionResponse


dp_real_link = "https://mobile.datpiff.com/mixtape/983402?trackid=1&platform=desktop"
dummy_text = "<blah blah blah>"
dummy_json_data = {"success": True, "data": "foo-bar"}

mocked_session = mockSessionResponse(
    status=200, text=dummy_text, json_data=dummy_json_data
)


class TestWebHandler(unittest.TestCase):
    HTML = webhandler.Html

    def test_Html_removes_ampersands_correctly(self):
        copyright = "&copy;"
        original_string = "copyright pydatpiff.inc"
        footer = "".join((copyright, original_string))
        results = self.HTML.remove_ampersands(footer)

        # test
        self.assertEqual(original_string, results[0])

        # test remove_ampersand_return type is a list
        self.assertIsInstance(results, list)
