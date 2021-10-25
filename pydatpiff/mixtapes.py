import re
from functools import wraps

from .backend.mixsetup import DOMProcessor
from .backend.utils import Selector
from .errors import MixtapesError
from .frontend.display import Print, Verbose
from .urls import Urls
from .utils.request import Session


class Mixtapes(object):
    category = list(Urls.category)

    def __new__(cls, *args, **kwargs):
        return super(Mixtapes, cls).__new__(cls)

    def __init__(self, category="", search="", limit=600, *args, **kwargs):
        """
        Mixtapes Initialization.

        :param: category - name of the catgeory to search from.
                            see Mixtapes.category

        :param: search - search for an artist or mixtape's name
        """
        super(Mixtapes, self).__init__(*args, **kwargs)
        self._session = Session()
        self._selected_category = category or "hot"
        self._selected_search = search
        self._max_mixtapes = limit
        self._session.clear_cache
        self._setup()

    def _setup(self):
        self._selectMixtape(str(self._selected_category), str(self._selected_search))
        self._setAttributeRegex()

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
    def validate_search(user_input, expected=str, min_characters=3):
        """Clean and force constraints on mixtape's search method.
        Args:
            user_input (str): user input
            expected (user_inputtype), optional): user_inputtype expected from user. Defaults to str.
            min_character (int, optional): miniumun character accept . Defaults to 3.
        """
        try:
            user_input = expected(user_input)
        except TypeError:
            raise MixtapesError(4, "Expected datatype: {}.".format(expected))
        if len(user_input) < min_characters:
            raise MixtapesError(
                5,
                """Not enough character: {}.\
                 Minimum characters limit is {}.""".format(
                    user_input, str(min_characters)
                ),
            )

        return user_input.strip() if expected == str else user_input

    def _perform_search(self, name):
        """
        Search for an artist or mixtape's name.

        :param: name - name of an artist or mixtapes name
        """
        name = str(name).strip()
        if not name:
            return

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
        if search:  # Search for an artist
            body = self._perform_search(self.validate_search(search))
            if not body or body is None:  # on failure return response from a category
                return self._selectMixtape("hot")
        else:  # Select from category instead of searching
            selector = Selector.filter_choices
            choice = selector(category, Urls.category) or selector("hot", Urls.category)
            body = self._session.method("GET", choice)
        self._request_response = body
        return body

    def _setAttributeRegex(self):
        """Initial class variable and set their attributes on page load up."""
        # all method below are property setter method
        # each "re string" get pass to the corresponding html response text

        self.artists = r'<div class\="artist">(.*[.\w\s]*)</div>'
        self.mixtapes = r'"\stitle\="listen to ([^"]*)">[\r\n\t\s]?.*img'
        self.links = r'title"><a href\="(.*[\w\s]*\.html)"'
        self.ratings = r'<div class\="text">Rating: <img.*alt=\"(\d)*.*"'
        self.views = r'<div class\="text">Listens: <span>([\d,]*)</span>'
        self.album_covers = 'icon\\smixtape.*src="(.*)"\\salt'
        if len(self) == 0:
            Verbose("No Mixtapes Found")
        else:
            Verbose("Found %s Mixtapes" % len(self))

    def _searchTree(f):
        """
        Wrapper function that parse and filter all requests response content.
        After parsing and filtering the responses text, it then creates a
        dunder variable from the parent function name.

        :param: f  (wrapper function)
         #----------------------------------------------------------
         example: "function()" will create an attribute "_function"
         #----------------------------------------------------------
        """

        @wraps(f)
        def inner(self, *args, **kwargs):
            name = f.__name__
            path = f(self, *args, **kwargs)
            pattern = re.compile(path)
            data = DOMProcessor(self._request_response, limit=self._max_mixtapes).findRegex(pattern)
            if hasattr(self, "_artists") and len(self) != 0:
                # we map all attributes length to _artists length
                try:
                    data = data[: len(self)]
                except:
                    pass

            dunder = "_" + name
            setattr(self, dunder, data)
            return data

        return inner

    @property
    def artists(self):
        """return all Mixtapes artists' name"""
        if hasattr(self, "_artists"):
            return self._artists

    @artists.setter
    @_searchTree
    def artists(self, path):
        return path

    @property
    def album_covers(self):
        if hasattr(self, "_album_covers"):
            return self._album_covers

    @album_covers.setter
    @_searchTree
    def album_covers(self, path):
        """Returns mixtapes album cover image"""
        return path

    @property
    def mixtapes(self):
        """Return all mixtapes name"""
        if hasattr(self, "_mixtapes"):
            return self._mixtapes

    @mixtapes.setter
    @_searchTree
    def mixtapes(self, path):
        """return all the mixtapes titles from web page"""
        return path

    @property
    def links(self):
        """Return all of the Mixtapes' url links"""
        if hasattr(self, "_links"):
            return self._links

    @links.setter
    @_searchTree
    def links(self, path):
        return path

    @property
    def ratings(self):
        if hasattr(self, "_ratings"):
            return self._ratings

    @ratings.setter
    @_searchTree
    def ratings(self, rate):
        return rate

    @property
    def views(self):
        """Return the views count of each mixtapes"""
        if hasattr(self, "_views"):
            return self._views

    @views.setter
    @_searchTree
    def views(self, path):
        return path

    def display(self):
        """Prettify all Mixtapes information and display it to screen"""
        links = self._links
        data = zip(self._artists, self._mixtapes, links, self._views)
        for count, (a, t, l, v) in list(enumerate(data, start=1)):
            Print(
                "# %s\nArtist: %s\nAlbum: %s\nLinks: %s\nViews: %s\n%s\n"
                % (count, a, t, "https://datpiff.com" + l, v, "-" * 60)
            )

    def _select(self, choice):
        """
        Queue and load  a mixtape to media player.
                            (See pydatpiff.media.Media.setMedia)

        :param: choice - (int) user selection by indexing an artist name or album name
                            (str)
        """
        # Return the user selection by either integer or str
        # we map the integer to artists and str to mixtapes
        if isinstance(choice, int):
            selector = Selector.select_from_index
        else:
            selector = Selector.select_from_choices

        selection = selector(choice, self.artists, self.mixtapes)
        if selection is None:
            Print(f"\nSelection not found\n{selector}")
            raise MixtapesError(1)

        return selection
