import logging
import re
from functools import wraps

import bs4

from pydatpiff.constants import ampersands
from pydatpiff.errors import Mp3Error
from pydatpiff.urls import Urls
from pydatpiff.utils.request import Session

logger = logging.getLogger(__name__)


def escape_html_characters(char_list):
    results = []
    if not isinstance(char_list, (list, tuple)):
        char_list = [char_list]

    for char in char_list:
        if char in ampersands:
            amps = ampersands.index(char)
            char = re.sub(amps, "", char)
        results.append(char)
    return results


class MixtapeScraper:
    _MAX_RETRY = 5
    _MAX_MIXTAPES_PER_PAGE = 52  # maximum amount of mixtapes available per Datpiff's Page

    def __init__(self, base_response, limit=600):
        self._base_response = base_response  # Session.response
        self._soup = bs4.BeautifulSoup(base_response.text, "html.parser")

        # prepare request session
        self._session = Session()

        self._total_mixtapes = 0  # total mixtapes found
        # total mixtapes requested by user
        self._MIXTAPE_LIMIT = limit if isinstance(limit, int) else 520  # 10 pages

        self._initialize_attributes()
        self._get_page_links()

    @property
    def _attribute_list(self):
        """Mixtape dunder Attributes"""
        return [
            "_artists",
            "_mixtapes",
            "_links",
            "_ratings",
            "_views",
            "_album_covers",
        ]

    def _initialize_attributes(self):
        """Invoke  mixtape's attributes. See: pydatpiff.mixtapes.Mixtape"""
        for attr in self._attribute_list:
            setattr(self, attr, [])

    def _setMedias_attributes(self, bs4_content_list):

        for content in bs4_content_list.findAll(class_="contentItemInner"):
            # set album covers
            self._album_covers.extend([elem.find("img").get("src") for elem in content.findAll(class_="contentThumb")])

            # set artists
            self._artists.extend([elem.text for elem in content.findAll(class_="artist")])

            # Set mixtapes and links
            links = [elem.find("a") for elem in content.findAll(class_="title")]

            self._mixtapes.extend([re.sub(r"listen\sto", "", link.get("title")).strip() for link in links])
            self._links.extend([link.get("href") for link in links])

            # Set ratings and views
            self._ratings.extend([int(re.match(r"\d*", content.find(class_="text").img.get("alt"))[0])])
            self._views.extend(
                [
                    int(
                        re.sub(
                            r"\D*",
                            "",
                            content.findAll(class_="text")[1].span.text,
                        )[0]
                    )
                ]
            )

    @property
    def total_mixtapes(self):
        if hasattr(self, "_total_mixtapes"):
            return self._total_mixtapes
        return 0

    @total_mixtapes.setter
    def total_mixtapes(self, count):
        if isinstance(count, int):
            self._total_mixtapes += count

    def _parse_mixtape_page(self, url):
        """
        Mixtape's initiator function used to parse mixtape's page
        and returns detail used to set Mixtape's attributes.

        Args:
            url (str): mixtapes' page link url

        Returns:
            [int]: total number of mixtape's on page
        """
        text = self._session.method("GET", url=url).text
        # fmt: off
        content_container_id = "leftColumnWide"  # Datpiff Mixtape's main content wrapper
        content_wrapper_class = 'contentListing'
        mixtapes_content_items = "contentItem"  # Mixtape' Content Wrapper
        # fmt: on
        try:
            # Using BeautifulSoap
            soup = bs4.BeautifulSoup(text, "html.parser")
            content_container = soup.find(id=content_container_id)
            if content_container:
                content_listing = content_container.find(class_=content_wrapper_class)
                mixtape_items = content_listing.findAll(class_=mixtapes_content_items)
                # Set total mixtapes found
                self.total_mixtapes = len(mixtape_items)

                # set attribute for Mixtape Class
                self._setMedias_attributes(content_listing)
        except:
            logger.exception("CacheContentError")
            return 0

    def _get_page_links(self):
        """
        Return a list of html page links from mixtapes. Mixtape._select_mixtape method.
        """
        BASE_URL = Urls.datpiff["base"]

        # Check if pagination links are available
        pagination = self._soup.find(class_="pagination")
        if not pagination:
            # cache the first page and return the initial response url
            self._parse_mixtape_page(self._base_response.url)
            return [self._base_response.url]

        # Next get all pagination links anchor href.
        """
            Since this class (MixtapeScraper) has to be initialized with a mixtape, we should already have the
            content from the first page link (Active Page). Although we already processed this content,
            we still include it to accurately count to total mixtapes found. We should not be worried about recalling
            this request, since our `Session` will cache the response if it has already been requested.
        """
        page_links = pagination.find(class_="links").findAll("a")
        page_links = [BASE_URL + link.get("href") for link in page_links]
        for page_number, link in enumerate(page_links, start=1):
            # get the page link and parse it
            self._parse_mixtape_page(link)

            # If the max mixtapes is reached, then return the content
            # from the current page
            if self.total_mixtapes >= self._MIXTAPE_LIMIT:
                return page_links[:page_number]

        try:
            # If the max mixtapes is not reached, then return the last page of mixtapes
            return page_links  # return [<initial-url>]]
        except IndexError:
            # if all fails, then return the initial url
            self._parse_mixtape_page(self._base_response.url)
            return [self._base_response.url]

    def _request_get(self, url):
        """
        Thread safe request session's method.

        This method is used to get content from Datpiff's Mixtape web page
        during threading operation - ThreadQueue method.  See:  pydatpiff.backend.utils.ThreadQueue

        Args:
        url (str) - mixtape's link

        Returns:
            (str) - HTTP response text
        """
        return self._session.method("GET", url).text


class MediaScraper:
    @staticmethod
    def wrapper(f):
        @wraps(f)
        def inner(obj):
            try:
                f(obj)
            except:
                raise AttributeError("Regex Error")
            else:
                return f(obj)

        return inner

    @staticmethod
    def get_uploader_name(string):
        """Return the name of the person whom upload the mixtape"""
        try:
            return re.search(r'<a.*href="/profile.*>(.*)</a>', string).group(1)
        except AttributeError:
            pass
        return ""

    @staticmethod
    def get_uploader_bio(string):
        try:
            desc = re.findall(r'og:description".*content\="(.*)"', string)
            if desc:
                return escape_html_characters(desc[-1])[0].strip()
        except AttributeError:
            pass
        return ""

    @staticmethod
    def get_album_suffix_number(string):
        return re.search(r"\.(\d*)\.html", string).group(1)

    @staticmethod
    def get_embed_player_id(text):
        return re.search(r"/mixtapes/([\w\/]*)", text).group(1)  # noqa

    @classmethod
    def get_song_titles(cls, text):
        songs = re.findall(r'"title":"(.*\w*)",\s?"artist"', text)
        songs = list(escape_html_characters(songs))
        return songs

    @classmethod
    def get_duration_from(cls, text):
        return re.findall(r'"duration">(.*\d*)<', text)

    def get_mp3_urls(text):
        try:
            return re.findall(r"fix.concat\(\s\'(.*\w*)\'", text)  # noqa
        except AttributeError:
            raise Mp3Error(4)
