from unittest import TestCase
from unittest.mock import Mock, patch

from pydatpiff.urls import Urls
from pydatpiff.utils import request
from pydatpiff.utils.request import Session
from tests.test_utils import BaseTest


class TestRequest(BaseTest, TestCase):
    def setUp(self):
        url = Urls.category["hot"]
        content = self.get_request_content("mixtape")
        self.response = self.mocked_response(content=content, url=url)

        Session.session.get = Mock(autospec=True, return_value=self.response)
        self.session = Session()

        self.maxDiff = None

    def test_session_is_mocked(self):
        url = Urls.category["hot"]
        response = self.session.method("GET", url)
        self.assertEqual(response.status_code, 200)

        for artist in self.artist_list:
            self.assertIn(artist, response.text)

    def test_request_response_are_cached(self):
        # put response in cache
        url = Urls.category["hot"]
        self.session.put_in_cache(url, self.response)

        # test response in cache is the correct response
        cache = self.session.get_from_cache(url)
        self.assertEqual(cache, self.response)

    @patch.object(request.Session, "put_in_cache", autospec=True)
    def test_request_clear_cache_when_MemoryError_occurs(self, put_in_cache):
        self.session._CACHE = {"some_url", "some_response"}
        put_in_cache.side_effect = MemoryError()
        with self.assertRaises(MemoryError):
            put_in_cache("some_url", "dokeooeoeokeook")
            cache = self.session._CACHE
            self.assertEqual(cache, {})

    def test_request_method_return_None_when_method_is_invalid(self):
        get_req = self.session.session.get = Mock(return_value=None)
        self.session._CACHE = {}
        args = ("some_invalid_method", "some_url")
        self.session.method(*args)

        self.assertTrue(get_req.called_once)
        self.assertTrue(get_req.called_with_args(*args))
