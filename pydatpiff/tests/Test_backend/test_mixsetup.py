import os
import sys
import unittest
from unittest.mock import Mock, patch, PropertyMock
from ...backend import mixsetup
from ...urls import Urls
from ...errors import MixtapesError
from ..test_utils import mockSessionResponse, mockRegex


dp_real_link = "https://mobile.datpiff.com/mixtape/983402?trackid=1&platform=desktop"
dummy_text = "<blah blah blah>"
dummy_json_data = {"success": True, "data": "foo-bar"}

mocked_session = mockSessionResponse(
    status=200, text=dummy_text, json=dummy_json_data, url="https://datpiff.com"
)

# mixsetup.Session = mocked_session
class TestDOMProcessor(unittest.TestCase):
    def setUp(self):
        self.session = patch.object(mixsetup, "Session", spec=True)
        self.session.method = Mock()
        self.session.method.text = Mock(return_value=mocked_session.text)
        self.session.return_value = mocked_session

        self.MOCKED_SESSION = self.session.start()
        self.getDOM
        self.addCleanup(patch.stopall)

    @property
    def getDOM(self):
        """helper function initialized mixsetup.Pages class"""
        self.MS = mixsetup.DOMProcessor(mocked_session)

    def test_Page_session_is_Mock(self):
        # test whether MS session is really mocked
        SESSION = self.MOCKED_SESSION()
        assert self.MS._session is SESSION

    def test_get_page_links(self):
        # test get_page_links returns a list containing the session.url when
        # it can not find regex pattern in session response  html content
        url = [Urls().url["base"]]
        MS = self.MS
        self.assertEqual([mocked_session.url], MS.get_page_links)

    def test_getHtmlResponse(self):
        # test if function return a value
        ms = mixsetup.DOMProcessor("whatever")
        gr = ms._getHtmlResponse = Mock(return_value=mocked_session.text)
        self.assertEqual(gr.return_value, self.session.method.text.return_value)
