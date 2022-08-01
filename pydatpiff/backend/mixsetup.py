import logging
import re

import bs4

from pydatpiff.urls import Urls
from pydatpiff.utils.request import Session

logger = logging.getLogger(__name__)


class DOMProcessor:
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
        """Mixtapes dunder Attributes"""
        return [
            "_artists",
            "_mixtapes",
            "_links",
            "_ratings",
            "_views",
            "_album_covers",
        ]

    def _initialize_attributes(self):
        """Invoke  mixtape's attributes. See: pydatpiff.mixtapes.Mixtapes"""
        for attr in self._attribute_list:
            setattr(self, attr, [])

    def _set_mixtapes_attributes(self, bs4_content_list):

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
        mixtapes_content_items = "contentItem"  # Mixtapes's Content Wrapper
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

                # set attribute for Mixtapes Class
                self._set_mixtapes_attributes(content_listing)
        except:
            logger.exception("CacheContentError")
            return 0

    def _get_page_links(self):
        """
        Return a list of html page links from mixtapes. Mixtapes._selectMixtape method.
        """
        try:
            BASE_URL = Urls.datpiff["base"]

            # Check if pagination links are available
            pagination = self._soup.find(class_="pagination")
            if not pagination:
                # cache the first page and return the initial response url
                self._parse_mixtape_page(self._base_response.url)
                return [self._base_response.url]

            # Next get all pagination links anchor href.

            # Since this class (DOMProcessor) has to be initialized with a mixtape
            # request's content (base_response), we should already have the content
            # from the first page link (Active Page). Although we already processed this content,
            # we still include it to accurately count to total mixtapes found.
            # No Worries about recalling this request, Session cache will reject
            # the request and return the cached response.
            page_link_urls = ["".join((BASE_URL, link)) for link in pagination.find(class_="links").findAll("a")]

            # iterate through each response (anchor link response)
            for page_number, link in enumerate(page_link_urls):
                self._parse_mixtape_page(link)
                # It mixtapes limit is reached, then return the content
                # from all previous page link
                if self.total_mixtapes <= self._MIXTAPE_LIMIT:
                    return page_link_urls[:page_number]

            # if forloop don't break then return all anchor urls
            return page_link_urls
        except:
            # Cache the first page and return the initial response url
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
