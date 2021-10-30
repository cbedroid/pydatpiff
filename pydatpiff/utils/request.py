import logging
import warnings

import requests
from requests.adapters import HTTPAdapter

from pydatpiff.errors import RequestError

# Set Request logging levels
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)


class Session:
    """Dynamic way to way to keep requests.Session through out whole programs."""

    # private
    _TOTAL_TIMEOUT = 0
    _MAX_RETRIES = 2
    _CACHE = {}

    # public
    TIMEOUT = 3  # 5 secs
    session = requests.Session()

    def __init__(self, *arg, **kwargs):
        transport_adapter = HTTPAdapter(pool_connections=50, pool_maxsize=50, max_retries=self._MAX_RETRIES)
        self.session.mount("https://", transport_adapter)

    @classmethod
    def put_in_cache(cls, url, response):
        try:
            url = url.strip()
            cls._CACHE[url] = response
        except MemoryError:
            cls.clear_cache()

    @classmethod
    def clear_cache(cls):
        """clear _CACHE to prevent memory error"""
        del cls._CACHE
        cls._CACHE = {}

    def get_from_cache(self, url):
        """Checks if url already have a response.
        Stop from calling the request method more than once.
        Great for saving mobile data on mobile devices.
        """
        url = str(url).strip()
        if url in self._CACHE.keys():
            return self._CACHE[url]

    def method(self, method, url, bypass=None, **kwargs):
        """urllib requests method"""
        valid_method = ["get", "post"]
        method = str(method).lower()

        if method not in valid_method:
            return

        cached_response = self.get_from_cache(url)
        if cached_response and method != "post":
            return cached_response

        try:
            # GET
            if method == "get":
                web = self.session.get(url, timeout=self.TIMEOUT, **kwargs)
            # POST
            if method == "post":
                web = self.session.post(url, timeout=self.TIMEOUT, **kwargs)

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            # first catch server connect error, then user's internet error
            if e is requests.exceptions.ReadTimeout:
                raise RequestError(1)

            # catch user's connection error
            self._TOTAL_TIMEOUT += 1
            if self._TOTAL_TIMEOUT >= 3:
                print("\n")  # need for spacing
                warn_msg = "\nWarning: Please check your internet connection !"
                warnings.warn(warn_msg)
                self._TOTAL_TIMEOUT = 0
            raise RequestError(2)

        except requests.exceptions.InvalidURL:
            raise RequestError(3)

        # process the request for HTTP Errors
        try:
            web.raise_for_status()
        except:
            raise RequestError(4)
        else:
            # cache the request response for later use cases
            self.put_in_cache(url, web)
            self._TOTAL_TIMEOUT = 0
        finally:
            return web
