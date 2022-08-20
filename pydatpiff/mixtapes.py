from pydatpiff.utils.utils import Select

from .backend.scraper import MixtapeScraper
from .errors import MixtapeError
from .frontend.screen import Verbose
from .urls import Urls
from .utils.request import Session


class Mixtape(MixtapeScraper):
    valid_categories = list(Urls.category)
    _default_category = "hot"
    _user_selected = _default_category  # user  category or search input

    def __init__(self, category=None, search=None, limit=None, *args, **kwargs):
        """
        Mixtape Initialization.

        :param: category - name of the category to search from.
                            see Mixtape.category

        :param: search - search for an artist or mixtape's name
        """
        self._session = Session()
        self._session.clear_cache()

        self._select_mixtape(category=category, search=search)

        initial_page_content = self._request_response
        super().__init__(initial_page_content, limit=limit)

        if not len(self):
            Verbose("No Mixtape Found")
        else:
            Verbose("Found %s mixtapes" % len(self))

    def __str__(self):
        prefix = getattr(self, "_user_selected", self._default_category)
        return f"{prefix.title()} {self.__class__.__name__}"

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
            raise MixtapeError(2, "Expected datatype: string")

        if len(user_input) < min_characters:
            raise MixtapeError(
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

    def _select_mixtape(self, category=None, search=None):
        """
        Initial setup. Gets all available mixtapes.

        :param: category - name of the category to search from.
                            (self Mixtape.category)
        :param: search - search for an artist or mixtape's name
        """
        if search:  # Search for an artist or mixtape
            filtered_search = self._validate_search(search)
            body = self._perform_search(filtered_search)
            self._user_selected = search  # capture user search input

        else:  # Selecting from category
            category = category or self._default_category
            if category.lower() not in self.valid_categories:
                category = self._default_category

            self._user_selected = category  # capture user category input
            choice = Select.by_choices(category, Urls.category)
            url = Urls.category[choice]  # get the url for the category
            body = self._session.method("GET", url)
        self._request_response = body
        return body

    @property
    def artists(self):
        """return all Mixtape artists' name"""
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
        """Return all of the Mixtape' url links"""
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
