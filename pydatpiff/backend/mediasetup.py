import re
import warnings

from pydatpiff.errors import DatpiffError, Mp3Error
from pydatpiff.urls import Urls
from pydatpiff.utils.request import Session

from .utils import Object
from .webhandler import MediaScrape

SERVER_DOWN_MSG = (
    "\n\t--- UNOFFICIAL DATPIFF MESSAGE --"
    "\nSorry, Its seems that Datpiff's server is down."
    " Please check back later "
)
# warnings.


class DatpiffPlayer:
    """Datpiff's frontend media player object"""

    # Flag for mobile version.
    # Fallback if desktop version is not working ('website issue')
    _USE_MOBILE = False

    def __init__(self, link):
        """
        Media player frontend for pydatpiff
        """
        # Setting  '_album_link' from "link", although the parent class
        # will set this on __init__ --> parent class "Album"
        # ... no biggie doe.. we're just making sure its set
        self._album_link = link
        self.create_album_link(link)
        self.__changeVersion()

    def __changeVersion(self):
        """
        Private function that will check program and determine
        which version ( desktop or mobile ) to use.

        As of July 10,2020, Datpiff's desktop version is broken,
        and is not populating album data.

        Data that is NOT being popluated are ONLY the followings:
          - Album.name
          - Mp3.songs

        All other function still work as intented.

        This function will check if an album name is populated correct.
        if not then mobile version will be used as a fallback
        """
        # we check if Album.name is populated, if not switch to mobile version
        try:
            if self.name:
                return
        except AttributeError:
            # TODO: Alert user about this issue
            pass
        self._USE_MOBILE = True

    @property
    def dpp_html(self):
        response = self._get_embeded_player_response
        if response:
            return response.text

    def create_album_link(self, album_id):
        """Creates a url link to Datpiff album's media player."""
        # July 10 2020 , This will fixed error with songs name not populating
        # if desktop verison fails, flag program to use Mobile version as a fallback
        version = "mobile" if self._USE_MOBILE else "embeds"
        return "".join(
            (
                "https://{}.datpiff.com/mixtape/".format(version),
                str(album_id),
                "?trackid=1&platform=desktop",
            )
        )

    @property
    def album_ID(self):
        """Album ID Number"""
        return MediaScrape.get_album_suffix_number(self._album_link)

    @property
    def _get_embeded_player_response(self):
        """return Datpiff player html contents"""
        """
         Note: Request Sessions are being cached for every request.
               If the url endpoint is found in the cached, the request
               will NOT be recalled.  Instead the cached response will be returned.
        """
        url = self.create_album_link(self.album_ID)
        try:
            return self._session.method("GET", url)
        except:
            warnings.warn(SERVER_DOWN_MSG)
            raise DatpiffError(1, "\nPlease check back later.")

    @property
    def bio(self):
        return MediaScrape.get_uploader_bio(self.dpp_html)

    @property
    def name(self):
        # for desktop verison issue we will use the mobile version
        if self._USE_MOBILE:
            name = re.search(r'og:title"\s*content\="(.*[\w\s]*)"', self.dpp_html).group(1)
        else:
            # desktop only
            name = re.search(r'title">(.*[\w\s]*)\</div', self.dpp_html).group(1)
        return name


class Mp3:
    def __init__(self, album):
        """
        Mp3 extracts and creates audio data.

        :param: album - Datpiff Album
                        [object]
        """
        if not getattr(album, "dpp_html", None):
            raise Mp3Error(1, "No album response found")

        self.album = album
        self.album_response = album.dpp_html

    def __len__(self):
        if self.songs:
            return len(self.songs)
        return 0

    def __str__(self):
        if getattr(self, "album"):
            return " ".join((str(self.album), "Mp3"))
        return "MP3"

    @property
    def song_duration(self):
        """Duration of songs"""
        # Tested July 10, 2020 This code is not implemented
        #  and has not been implemented since duration of project
        #  TODO: USE IT OR GET RID OF IT
        # --
        # This methodology will implement in backend/audio/baseplayer instead
        # Tested and this code will cause error using desktop (default) version
        return MediaScrape.get_duration_from(self.album_response)

    @property
    def songs(self):
        """Songs from mixtape album."""
        return MediaScrape.get_song_titles(self.album_response)

    @property
    def urlencode_track(self):
        """
        Url encodes all mp3 songs' name
        Each song will be prefix with its track index and url encoded.

        return: - A list of url encoded songs.
                return datatype: list
        Ex:-02) - Off the Wall.mp3' -->  02)%20-%20Off%20the%20Wall.mp3
        """
        songs = MediaScrape.get_mp3_urls(self.album_response)
        return [re.sub(" ", "%20", song) for song in songs]

    @property
    def album_id(self):
        """
        Media Album reference ID number
        Ex: 6/m1393dba
        """
        try:
            return MediaScrape.get_embed_player_id(self.album_response)
        except:
            Mp3Error(1)

    @property
    def mp3_urls(self):
        prefix = "https://hw-mp3.datpiff.com/mixtapes/"
        for track in self.urlencode_track:
            endpoint = "{}{}".format(self.album_id, track)
            yield "".join((prefix, endpoint))


class Album(DatpiffPlayer):
    """
    Renders Datpiff's Mixtape page and create URI link to it's media player object.
    Data from URI link will be process and use to populate data for mixtapes. This data
    includes:
        Album uploader's name and bio
        Album's name and songs
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_session"):
            cls._session = Session()
        return super(Album, cls).__new__(cls)

    def __init__(self, link):
        self.link = "".join((Urls.url["album"], link))
        super(Album, self).__init__(self.link)

    def __str__(self):
        return self.name

    @property
    def album_html(self):
        """
        Return the requests response from the current Mixtapes link
            See __init__ or mixtapes.Mixtapes.links.
        """
        # we dont have to worry about recalling this requests method
        # multiple times,because the session will return the cache response if
        # the response has already been downloaded

        response = self._session.method("GET", self.link)
        if response:
            return response.text
        return " "

    @property
    def uploader(self):
        return MediaScrape.get_uploader_name(self.album_html)

    @classmethod
    def searchFor(cls, links, song, *args, **kwargs):
        """
        Search through all Albums and return all Albums
        that contains similiar songs' title.

        :param: song - title of the song to search for
        :param: links - all mixtapes links
        """
        index, link = links
        album = cls(link)
        tracks = Mp3(album).songs
        for track in tracks:
            if song in Object.strip_and_lower(track):
                return {"ablumNo": index, "album": album.name, "song": track}
