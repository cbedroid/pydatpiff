from unittest import TestCase
from unittest.mock import Mock

from pydatpiff.backend import mixsetup
from pydatpiff.urls import Urls
from tests.test_utils import BaseTest


class TestMixSetup(BaseTest, TestCase):
    def setUp(self):
        content = self.get_request_content("mixtape")
        method = mixsetup.Session.method = Mock(autospec=True)
        method.return_value = self.mocked_response(content=content)

        response = self.mocked_response(content=content)
        self.DOM = mixsetup.DOMProcessor(response)

    def test_mixtapes_total(self):
        hot_category_url = Urls.category["hot"]
        total_mixtapes = self.DOM._get_mixtapes_total(hot_category_url)

        self.assertEqual(total_mixtapes, 12)

    def test_mixsetup_get_page_links_return_mixtapes_pages(self):
        page_links = self.DOM.get_page_links
        self.assertGreaterEqual(len(page_links), 1)

    def test_get_HtmlResponse_returns_content(self):
        url = Urls.category["hot"]
        html = self.DOM._getHtmlResponse(url)
        self.assertIsNotNone(html)

    def test_get_HtmlResponse_contains_correct_content(self):
        url = Urls.category["hot"]
        html = self.DOM._getHtmlResponse(url)

        mixtapes_and_artists = zip(self.mixtape_list, self.artist_list)
        for mixtape, artist in mixtapes_and_artists:
            self.assertIn(mixtape, html)
            self.assertIn(artist, html)
