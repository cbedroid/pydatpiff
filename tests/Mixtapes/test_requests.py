from unittest import TestCase
from unittest.mock import Mock, patch

from pydatpiff.urls import Urls
from pydatpiff.utils import request
from tests.utils import BaseTest


class TestRequest(BaseTest, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Mocked `urllib requests.Session`
        url = Urls.category["hot"]
        content = cls.get_request_content("mixtape")
        cls.response = cls.mocked_response(content=content, url=url)
        request.Session.session.get = Mock(autospec=True, return_value=cls.response)

    def test_request_response_are_cached_after_request_completes(self):
        # put response in cache
        url = Urls.category["hot"]
        session = request.Session()
        session.put_in_cache(url, self.response)

        # test response in cache is the correct response
        cache = session.get_from_cache(url)
        self.assertEqual(cache, self.response)

    @patch.object(request.Session, "put_in_cache", autospec=True)
    def test_cache_is_cleared_when_MemoryError_occurs(self, mocked_put_in_cache):
        mocked_put_in_cache.side_effect = MemoryError()
        args = ("some_url", "dokeooeoeokeook")

        with self.assertRaises(MemoryError):
            request.Session.put_in_cache(*args)
        self.assertEqual(request.Session._CACHE, {})
        mocked_put_in_cache.assert_called_once_with(*args)

    def test_request_method_return_None_when_method_is_invalid(self):
        session = request.Session()
        session.method = Mock(autospec=True)
        session.method.return_value = None
        kwargs = {"method": "unknown", "url": "http://localhost.com"}
        response = session.method(**kwargs)
        self.assertEqual(response, None)
        session.method.assert_called_once_with(**kwargs)
