import re

from pydatpiff.constants import SERVER_DOWN_MSG
from pydatpiff.errors import DatpiffError, Mp3Error
from pydatpiff.urls import Urls
from pydatpiff.utils.request import Session
from pydatpiff.utils.utils import Object

from .scraper import MediaScraper


class DatpiffPlayer:
    """
    Datpiff's frontend media player object
    """

    # Flag for mobile's version.
    # Fallback if desktop version is not working ('website issue')
    _USE_MOBILE = False

    def __init__(self, link):
        raise NotImplementedError("This class is not yet implemented")

    @property
    def name(self):
        # for desktop version issue we will use the mobile version
        try:
            return (
                re.search(r'og:title"\s*content\="(.*[\w\s]*)Mixtape*"', self.embedded_player_content).group(1).strip()
            )
        except AttributeError:
            return re.search(r'title">(.*[\w\s]*)</div', self.embedded_player_content).group(1).strip()
        except:
            raise Mp3Error(3, "Could not find album's name")

    @property
    def embedded_player_content(self):
        """Returns Datpiff embedded player response text"""
        # Note: Request Sessions are being cached for every request.
        #      If the url endpoint is found in the cached, the request
        #      will NOT be recalled.  Instead, the cached response will be returned.
        url = self.build_album_url(self.album_ID)
        try:
            return self._session.method("GET", url).text
        except:  # noqa
            raise DatpiffError(1, SERVER_DOWN_MSG)

    @property
    def album_ID(self):
        """Album ID Number"""
        return MediaScraper.get_album_suffix_number(self.link)

    @property
    def bio(self):
        return MediaScraper.get_uploader_bio(self.embedded_player_content)

    def _check_datpiff_version(self):
        """
        function that will check program and determine
         which version ( desktop or mobile ) to use.

         As of July 10, 2020, Datpiff's desktop's version is broken,
         and is not populating album data.

         Data that is NOT being populated are ONLY the followings:
           - Album.name
           - Mp3.songs

         All others function still work as expected.

         This function will check if an album name is populated correct.
         if not then mobile version will be used as a fallback
        """
        # we check if Album.name attribute exists.
        # If it doesn't, we switch to mobile version

        if not getattr(self, "name", None):
            self._USE_MOBILE = True

    @classmethod
    def build_album_url(cls, album_id):
        """Creates album url link from Datpiff's embedded music player."""

        # July 10, 2020 , This will fix error with songs name not populating
        # if desktop version fails, flag program to use Mobile version as a fallback
        version = "mobile" if cls._USE_MOBILE else "embeds"
        return "".join(
            (
                "https://{}.datpiff.com/mixtape/".format(version),
                str(album_id),
                "?trackid=1&platform=desktop",
            )
        )


class Album(DatpiffPlayer):
    """
    Renders Datpiff's Mixtape page and create URI link to its media player object.
    Data from URI link will be process and use to populate data for mixtapes. This data
    includes:
        Album uploader name and bio
        Album's name and songs
    """

    _session = Session()

    def __init__(self, link):
        """
        Media player Album object constructor.
        :param link: Link to the media player page.
        """
        self._check_datpiff_version()
        self.link = "".join((Urls.datpiff["album"], link))

        # try:
        #     super(Album, self).__init__(self.link)
        # except TypeError:
        #     warnings.warn(SERVER_DOWN_MSG)
        #     raise DatpiffError(1, SERVER_DOWN_MSG)

    def __str__(self):
        return self.name

    @property
    def album_html(self):
        """
        Return the requests' response from the current Mixtape link
            See __init__ or mixtapes.Mixtape.links.
        """
        # we don't have to worry about recalling this requests method
        # multiple times,because the session will return the cache response if
        # the response has already been downloaded

        response = self._session.method("GET", self.link)
        if response:
            return response.text
        return " "

    @property
    def uploader(self):
        return MediaScraper.get_uploader_name(self.album_html)

    @classmethod
    def lookup_song(cls, links, song, *args, **kwargs):
        """
        Search through all Albums and return all Albums
        that contains similar songs' title.

        Args:
                 song (string) - title of the song to search for
                 links (string) - all mixtapes links
        """
        index, link = links
        album = cls(link)
        tracks = Mp3(album).songs
        for track in tracks:
            if song in Object.strip_and_lower(track):
                return {"index": index, "album": album.name, "song": track}


class Mp3:
    def __init__(self, album):
        if not getattr(album, "embedded_player_content", None):
            raise Mp3Error(1, "No album response found")

        self.album = album
        self.album_response = album.embedded_player_content

    def __len__(self):
        if self.songs:
            return len(self.songs)
        return 0

    def __str__(self):
        if getattr(self, "album"):
            return " ".join((str(self.album), "Mp3"))
        return "MP3"

    @property
    def songs(self):
        """Returns all songs name from album."""
        return MediaScraper.get_song_titles(self.album_response)

    @property
    def urlencode_track(self):
        """Url encode audio url"""
        songs = MediaScraper.get_mp3_urls(self.album_response)
        return [re.sub(" ", "%20", song) for song in songs]

    @property
    def album_id(self):
        """Media Album reference ID number Ex: 6/m1393dba"""
        try:
            return MediaScraper.get_embed_player_id(self.album_response)
        except:
            Mp3Error(1)

    @property
    def mp3_urls(self):
        prefix = "https://hw-mp3.datpiff.com/mixtapes/"
        for track in self.urlencode_track:
            endpoint = "{}{}".format(self.album_id, track)
            yield "".join((prefix, endpoint))
