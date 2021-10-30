from .backend.mixsetup import DOMProcessor
from .backend.utils import Filter
from .errors import MixtapesError
from .frontend.screen import Verbose
from .urls import Urls
from .utils.request import Session


class Mixtapes(DOMProcessor):
    category = list(Urls.category)

    def __init__(self, category="hot", search="", limit=None, *args, **kwargs):
        """
        Mixtapes Initialization.

        :param: category - name of the category to search from.
                            see Mixtapes.category

        :param: search - search for an artist or mixtape's name
        """
        self._session = Session()
        self._session.clear_cache

        self._selectMixtape(category=category, search=search)

        initial_page_content = self._request_response
        super().__init__(initial_page_content, limit=limit)

        # self._setAttributeRegex()

        if not len(self):
            Verbose("No Mixtapes Found")
        else:
            Verbose("Found %s Mixtapes" % len(self))

    def __repr__(self):
        return "{}('hot')".format(self.__class__.__name__)

    def __str__(self):
        prefix = self._selected_search or self._selected_category
        return "{} {}".format(prefix.title(), self.__class__.__name__)

    def __len__(self):
        if hasattr(self, "_artists"):
            if self._artists is not None:
                return len(self._artists)
        return 0

    @staticmethod
    def _validate_search(user_input):
        """Clean and force constraints on mixtape's search method.
        Args:
            user_input (str): user input
        """

        min_characters = 3
        if not isinstance(user_input, str):
            raise MixtapesError(2, "Expected datatype: string")

        if len(user_input) < min_characters:
            raise MixtapesError(
                3,
                """Not enough character: {}.\
                 Minimum characters limit is {}.""".format(
                    user_input, str(min_characters)
                ),
            )

        return user_input.strip()

    def _perform_search(self, name):
        """
        Search for an artist or mixtape's name.

        :param: name - name of an artist or mixtapes name
        """
        name = str(name).strip()
        Verbose("\nSearching for %s mixtapes ..." % name.title())
        url = Urls.datpiff["search"]
        return self._session.method("POST", url, data=Urls.payload(name))

    def _selectMixtape(self, category="hot", search=None):
        """
        Initial setup. Gets all available mixtapes.

        :param: category - name of the category to search from.
                            (self Mixtapes.category)
        :param: search - search for an artist or mixtape's name
        """
        if search:  # Search for an artist or mixtape
            filtered_search = self._validate_search(search)
            body = self._perform_search(filtered_search)

        else:  # Selecting from category
            choice = Filter.choices(category, Urls.category, fallback="hot")
            body = self._session.method("GET", choice)
        self._request_response = body
        return body

    @property
    def artists(self):
        """return all Mixtapes artists' name"""
        if hasattr(self, "_artists"):
            return self._artists

    @property
    def album_covers(self):
        if hasattr(self, "_album_covers"):
            return self._album_covers

    @property
    def mixtapes(self):
        """Return all mixtapes name"""
        if hasattr(self, "_mixtapes"):
            return self._mixtapes

    @property
    def links(self):
        """Return all of the Mixtapes' url links"""
        if hasattr(self, "_links"):
            return self._links

    @property
    def ratings(self):
        if hasattr(self, "_ratings"):
            return self._ratings

    @property
    def views(self):
        """Return the views count of each mixtapes"""
        if hasattr(self, "_views"):
            return self._views
