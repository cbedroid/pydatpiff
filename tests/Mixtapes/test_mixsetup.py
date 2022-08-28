from unittest import TestCase
from unittest.mock import Mock

from pydatpiff.backend import scraper
from pydatpiff.urls import Urls
from tests.utils import BaseTest


class TestScraper(BaseTest, TestCase):
    def setUp(self):
        content = self.get_request_content("mixtape")
        method = scraper.Session.method = Mock(autospec=True)
        method.return_value = self.mocked_response(content=content)

        response = self.mocked_response(content=content)
        self.DOM = scraper.MixtapeScraper(response)

    def test_mixtapes_total_is_correct(self):
        hot_category_url = Urls.category["hot"]
        self.DOM._parse_mixtape_page(hot_category_url)
        total_mixtapes = self.DOM.total_mixtapes

        self.assertEqual(total_mixtapes, 24)

    def test_mixtape_scraper_return_no_mixtapes_when_Datpiff_mixtapes_(self):
        # mocked _parse_mixtapes request response text so
        # BeautifulSoup can not find the mixtape main container and exit early
        method = self.DOM._session.method = Mock(autospec=True)
        method.text = "<html></html>"
        hot_category_url = Urls.category["hot"]

        # reset the total mixtapes since self.DOM is already initialized
        del self.DOM._total_mixtapes
        self.DOM._parse_mixtape_page(hot_category_url)
        total_mixtapes = self.DOM.total_mixtapes
        self.assertEqual(total_mixtapes, 0)

    def test_mixtape_scaper_find_mixtapes_pages_links(self):
        page_links = self.DOM._get_page_links()
        self.assertGreaterEqual(len(page_links), 1)

    def test_mixtape_scraper_get_request_method_return_valid_html_content(self):
        url = Urls.category["hot"]
        html = self.DOM._request_get(url)
        self.assertIsNotNone(html)
        self.assertIn("contentListing", html)
        self.assertIn("contentItem", html)

    def test_mixtape_scraper_has_mixtapes_page_contains_correct_artists_and_mixtapes(self):
        url = Urls.category["hot"]
        html = self.DOM._request_get(url)

        mixtapes_and_artists = zip(self.mixtape_list, self.artist_list)
        for mixtape, artist in mixtapes_and_artists:
            self.assertIn(mixtape, html)
            self.assertIn(artist, html)

    def test_mixtape_scraper_get_page_links_return_page_links(self):
        url_links = self.DOM._get_page_links()
        self.assertGreaterEqual(len(url_links), 1)
