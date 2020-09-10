import re
from ..urls import Urls
from ..utils.request import Session
from .webhandler import Html
from .config import User, Datatype, Queued
from ..errors import MixtapesError

TIME_RAN = 0


class DOMProcessor:
    RETRY = 5  # TODO: fix retry:: some reason findRegex fails on first try

    def __init__(self, base_response, limit=600):
        self.base_response = base_response  # Session.response
        self.base_url = Urls().url["base"]
        self._session = Session()

        # maximum amount of available mixtapes possible
        self.MAX_MIXTAPES = limit if isinstance(limit, int) else 600
        self.trys = 1

    @staticmethod
    def countMixtapes(url):
        """Count the number of mixtapes available per page.

      Args:
          url (str): mixtapes' page link url

      Returns:
          [int]: total number of mixtape's on page
      """
        content = self._session.method("GET", url=url).text
        try:
            filtered_content = re.search(
                "(.*)rightColumnNarrow", text, re.DOTALL
            ).group(1)

            total = re.findall('icon\\smixtape.*src="(.*)"\\salt', filtered_content)
            return len(total)
        except:
            return 0

    @property
    def get_page_links(self):
        """
        Return a list of html page links from mixtapes.Mixtapes._getMixtapeResponse method.
        """
        try:
            """
                What we are trying to accomplish.
                ---------------------------------
            On pydatpiff.Mixtape startup, once a user select a category or 
            search for an artist. We then grab the content from that reponse.
            The initial request should return the FIRST page of the website.
            DAMN IT,we are greedy and we want them all!! So we parse through
            the content and search for any album links belonging to the artist.
            """

            # Get page links navigation DOM element from response
            navigations_links = re.findall(
                r'class\="links"(.*[\n\r]*.*\d)*</a>', self.base_response.text
            )

            # map navigation link's anchor tags to base urls
            page_link_urls = [
                re.search('href\=.*/(.*=\d{1,2})"', x).group(1)
                for x in navigations_links[0].split("</a>")
            ]

            """
                # OPTIMIZE SPEED WHEN LIMITING MIXTAPES SEARCHES
               NOTE: The website maximum mixtapes per page is 16 columns * 4rows 
                     Since each album will have a cover image, we can use this as
                     a map to get the max album per page. This will help guide us 
                     and give us an accurate break point to return data sooner.
                     #So we can break out of the search once we reach the user's 
                     #maximum mixtapes requested. 
                     #Dividing User max mixtapes requested by the website maximum 
                     #mixtapes per page should give us an accurate break point.
            """
            MAX_PER_PAGE = 64
            page_limit = int(self.MAX_MIXTAPES / MAX_PER_PAGE)
            page_limit = page_limit if page_limit > 1 else 1

            # map the page_link_urls to the base_url
            from time import time

            global TIME_RAN
            TIME_RAN += 1
            start = time()
            pagelinks = []
            mixtapes_founded = 0  # record the number of mixtapes found
            for page_number, link in enumerate(page_link_urls, start=1):
                plu = "".join((self.base_url, link))
                pagelinks.append(plu)
                mixtapes_founded += self.countMixtapes(plu)

                if mixtapes_found >= page_limit:
                    return pagelinks

            # return [''.join((self.base_url,link)) for link in page_link_urls]
        except:
            # if No page numbers in original url text,then return the original url
            return [self.base_response.url]

    def _getHtmlResponse(self, url):
        """
        Calls requests 'GET' method and returns the response content.
        This function should only be called when using Queued method.

        :param: url - mixtape's link
            :datatype: html formatted string
        """
        return self._session.method("GET", url).text

    def findRegex(self, re_string, bypass=False):
        """
        Uses Regex pattern to return the matching html data from each mixtapes
        :params: re_string - Regex pattern 
        :return: list object

        :EXAMPLE:
            re_string = '<div class\="artist">(.*[.\w\s]*)</div>'
            This re_string will return all of the artist names from 
            the Mixtapes web page (see _getHtmlResponse for Mixtapes web page link).
        """
        data = []
        re_Xpath = re.compile(re_string)
        # each page requests response data
        # Map each page links url to request.Session and
        # place Session in 'queue and thread'
        lrt = Queued(self._getHtmlResponse, self.get_page_links).run()
        list_response_text = Datatype.removeNone(lrt)

        # Remove all unwanted characters from Xpath
        [
            data.extend(
                list(
                    Html.remove_ampersands(pat.group(1))[0]
                    for pat in re_Xpath.finditer(RT)
                    if pat is not None
                )
            )
            for RT in list_response_text
        ]

        # hackable way to fix this function when its not returning data on first try
        # recalling the function if its returns None
        if not data:
            if self.trys < self.RETRY:
                self.trys += 1
                return self.findRegex(re_string)
            else:
                raise MixtapesError(3)
        elif len(data) < self.MAX_MIXTAPES and not bypass:
            # Try to get the maximum amount of mixtapes
            # Since the first time this function is called, the data weirdly return None
            # We keep trying until we get the max amount of mixtapes

            if self.trys < self.RETRY:
                self.trys += 1
                return self.findRegex(re_string)
            else:
                # print('Fuck it')
                return self.findRegex(re_string, True)
        return data[: self.MAX_MIXTAPES]
