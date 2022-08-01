import io
import os

from .backend.audio.player import Player
from .backend.filehandler import Path, Tmp, file_size
from .backend.mediasetup import Album, Mp3
from .backend.utils import Filter, Object, Threader, ThreadQueue
from .errors import MediaError
from .frontend import screen
from .mixtapes import Mixtapes
from .urls import Urls
from .utils.request import Session

Verbose = screen.Verbose


class Media:
    """Media player that control the songs selected from Mixtapes"""

    player = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "__tmpfile"):
            Tmp.removeTmpOnStart()
            cls.__tmpfile = Tmp.create()

        player = kwargs.get("player", "mpv")
        cls.player = Player.getPlayer(player)

        return super(Media, cls).__new__(cls)

    def __str__(self):
        album_name = self._album_name
        if album_name:
            return "{} Mixtape".format(album_name)
        return str(self.mixtapes)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.mixtapes.__class__)

    def __len__(self):
        if hasattr(self, "songs"):
            return len(self.songs)
        else:
            return 0

    def __init__(self, mixtapes=None, pre_select=None, player="mpv", **kwargs):
        """
        Initialize media player and load all mixtapes.

        Args:
            mixtapes (instance class) -- pydatpiff.Mixtapes instance (default: {None})
            pre_select (Integer,String) --  pre-selected mixtape's album, artist,or mixtapes.
                    See media.SetMedia for more info (default: None - Optional)

        Raises:
            MediaError: Raises MediaError if mixtapes is not an subclass of pydatpiff.Mixtapes.
        """
        self._session = Session()
        self.mixtapes = mixtapes
        self._artist_name = None
        self._album_name = None
        self._current_index = None
        self._selected_song = None
        self.__cache_storage = {}

        # Check if mixtape is valid
        self.__isMixtapesObject(mixtapes)

        Verbose("Media initialized")

        if pre_select:  # Run setMedia with argument here
            # This step is optional for users, but can save an extra setup
            # when selecting an album in setMedia.
            self.setMedia(pre_select)

    def _select(self, choice):
        """
        Queue and load  a mixtape to media player.
                            (See pydatpiff.media.Media.setMedia)

        :param: choice - (int) user selection by indexing an artist name or album name
                            (str)
        """
        # Map user selection according to the incoming datatype.
        # We map an integer to an artist and str to a mixtape.
        if hasattr(self, "mixtapes"):
            if isinstance(choice, int):
                selection = Filter.get_index(choice, options=self.mixtapes.artists)
            else:
                options = [self.mixtapes.artists, self.mixtapes.mixtapes]
                selection = Filter.get_indexOf(choice, options=options)

            return selection

    def setMedia(self, mixtape):
        """
        Initialize and set the an Album to Media Player.
        A pydatpiff.mixtapes.Mixtape's album will be load to the media player.

        Args:
            selection - pydatpiff.Mixtapes album's name or artist's name.
                int - will return the Datpiff.Mixtape artist at that index.
                str - will search for an artist from Mixtapes.artists (default)
                    or album from Mixtapes.album.

                See pydatpiff.mixtape.Mixtapes for album or artist selection
        """

        # Mixtape's class will handle errors and None value

        mixtape_index = self._select(mixtape)

        # set up all Album's Info
        total_mixtape = len(self.mixtapes) - 1
        if mixtape_index > total_mixtape:
            mixtape_index = total_mixtape

        # set Media's Mixtapes object attributes
        url = self.mixtapes._links[mixtape_index]
        self.url = "".join((Urls.datpiff["base"], url))

        self.artist = self.mixtapes.artists[mixtape_index]
        self.album_cover = self.mixtapes.album_covers[mixtape_index]

        # set Media's Album detail attributes
        self.album = Album(url)
        self._Mp3 = Mp3(self.album)

        # get the album's uploader
        self.uploader = self.album.uploader
        # get album bio
        self.bio = self.album.bio

        Verbose("Setting Media to %s - %s" % (self.artist, self.album))

    def __isMixtapesObject(self, instance):
        """Verify subclass is an instance of mixtapes' class

        Args:
            instance {instance class} -- pydatpiff's Mixtapes instance

        Returns:
            Boolean -- True or False if instance is subclass of pydatpiff Mixtape class
        """
        if not instance:
            raise MediaError(1)

        if not issubclass(instance.__class__, Mixtapes):
            raise MediaError(2, '"mixtape" must be Mixtapes object ')

    def findSong(self, songname):
        """
         Search through all mixtapes songs and return all songs
         with songname

        Args:
            songname {str} -- song to search for.

        Returns:
            tuple -- returns a tuple containing mixtapes data (index,artist,album) from search.
        """

        # NOTE: Take a look at this video by James Powell
        # https://www.youtube.com/watch?v=R2ipPgrWypI&t=1748s at 55:00.
        songname = Object.strip_and_lower(songname)
        Verbose("\nSearching for song: %s ..." % songname)
        links = self.mixtapes.links
        links = list(enumerate(links, start=1))
        results = ThreadQueue(Album.searchFor, links).execute(songname)
        if not results:
            Verbose("No song was found with the name: %s " % songname)
        results = Object.removeNone(results)
        return results

    def __index_of_song(self, select):
        """
        Parse all user input and return the correct song index.
        :param select: -  Media.songs name or index of Media.songs
               datatype: int: must be numerical
                         str: artist,mixtape, or song name
        """
        try:
            if isinstance(select, int):
                return Filter.get_index(select, self.songs)
            return Filter.get_indexOf(select, self.songs)
        except MediaError:
            raise MediaError(5)

    @property
    def artist(self):
        """Return the current artist name."""
        if not hasattr(self, "_artist_name"):
            self._artist_name = None
        return self._artist_name

    @artist.setter
    def artist(self, name):
        self._artist_name = name

    @property
    def album(self):
        """Return the current album name."""
        if not hasattr(self, "_album_name"):
            self._album_name = None
        return self._album_name

    @album.setter
    def album(self, name):
        self._album_name = name

    @property
    def album_cover(self):
        if hasattr(self, "_album_cover"):
            return self._album_cover

    @album_cover.setter
    def album_cover(self, url):
        self._album_cover = url

    @property
    def songs(self):
        """Return all songs from album."""
        if not hasattr(self, "_Mp3"):
            extra_message = '\nSet media by calling -->  Media.setMedia("some_mixtape_name")'
            raise MediaError(3, extra_message)
        return self._Mp3.songs

    @property
    def mp3_urls(self):
        """Returns all parsed mp3 url"""
        return list(self._Mp3.mp3_urls)

    def show_songs(self):
        """Pretty way to Print all song names"""
        try:
            songs = self.songs
            [Verbose("%s: %s" % (a + 1, b)) for a, b in enumerate(songs)]
        except TypeError:
            Verbose("Please set Media first\nNo Artist name")

    @property
    def song(self):
        """Returns the current song set by user."""
        return self._selected_song

    @song.setter
    def song(self, name):
        """
        Set current song
        name - name of song or song's index
        """
        index = self.__index_of_song(name)
        if index is not None:
            self._selected_song = self.songs[index]
            self._current_index = index
        else:
            Verbose("\n\t song was not found")

    def _cacheSong(self, songname, content):
        """
        Preserve the data from song and store it for future calls.
         This prevents calling the requests function again for the same song.
         Each data from a song will be stored in __cache_storage for future access.

        Args:
            songname (str):  name of song
            content (byte): song's audio content
        """
        name = "-".join((self.artist, songname))
        try:
            self.__cache_storage[name] = content
        except MemoryError:
            self.__cache_storage = {}

    def _retrieveFromCache(self, songname):
        """Retrieve song's audio content from cache
        Args:
            songname (str): name of song

        Returns:
            Http response : A http response containing the song's audio contents.
        """
        requested_song = "-".join((self.artist, songname))
        if hasattr(self, "__cache_storage"):
            if requested_song in self.__cache_storage:
                return self.__cache_storage.get(requested_song)

    def _writeAudio(self, track):
        """Write mp3 audio content to IO Bytes stream.
        Args:
            track (int,string): Name or index of song.

        Returns:
            BytesIO: A file-like API for reading and writing bytes objects.
        """

        selection = self.__index_of_song(track)
        if selection is None:
            raise MediaError("Song not found")

        self.__song_index = selection
        link = self.mp3_urls[selection]

        songname = self.songs[selection]
        self.song = selection + 1

        # Get/Set song's content in cached
        response = self._retrieveFromCache(songname)
        if not response:
            response = self._session.method("GET", link)
            self._cacheSong(songname, response)

        return io.BytesIO(response.content)

    @property
    def autoplay(self):
        """Continuously play song from current album."""
        if hasattr(self, "_auto_play"):
            self.player._media_autoplay = self._auto_play
            return self._auto_play

    @autoplay.setter
    def autoplay(self, auto=False):
        """Sets the autoplay function.

        auto - disable or enable autoplay
                 datatype: boolean
                 default: False
        """
        self._auto_play = auto
        self._continuosPlay()
        if auto:
            Verbose("\t----- AUTO PLAY ON -----")
        else:
            Verbose("\t----- AUTO PLAY OFF -----")

    @Threader
    def _continuosPlay(self):
        """
        Automatically play each song from Album when autoplay is enable.
        """
        if self.autoplay:
            total_songs = len(self)
            if not self.song:
                Verbose("Must play a song before setting autoplay")
                return

            track_number = self.__index_of_song(self.song) + 2
            if track_number > total_songs:
                Verbose("AutoPlayError: Current track is the last track")
                self.autoplay = False
                return

            while self.autoplay:
                current_track = self.__index_of_song(self.song) + 1
                stopped = self.player._state.get("stop")
                if stopped:
                    next_track = current_track + 1

                    if next_track > total_songs:
                        Verbose("No more songs to play")
                        self.autoplay = False
                        break

                    Verbose("Loading next track")
                    Verbose("AUTO PLAY ON")
                    self.play(next_track)
                    while self.player._state["stop"]:
                        pass

    def play(self, track=None, demo=False):
        """Play selected mixtape's track

        Args:
            track (int,string)- name or index of song.
            demo (bool, options) - True: demo buffer of song (default: False).
                False: play full song

        """

        if not track:
            Verbose("\n\t -- No song was entered --")
            return

        if self.player is None:
            extended_msg = "Audio player is incompatible with device"
            raise MediaError(6, extended_msg)

        if isinstance(track, int):
            if track > len(self):
                track = len(self)

        try:
            content = self._writeAudio(track).read()
        except Exception:
            Verbose("\n\t-- No song was found --")
            return

        songname = self.songs[self.__song_index]
        track_size = len(content)
        # play demo or full song
        if not demo:  # demo whole song
            chunk = content
            buffer = int(track_size)
        else:  # demo partial song
            buffer = int(track_size / 5)
            start = int(buffer / 5)
            chunk = content[start : buffer + start]
        size = file_size(buffer)

        # write song to file
        Path.writeFile(self.__tmpfile.name, chunk, mode="wb")

        # display message to user
        screen.display_play_message(self.artist, self.album, songname, size, demo)

        song = " - ".join((self.artist, songname))
        self.player.setTrack(song, self.__tmpfile.name)
        self.player.play

    def download(self, track=None, rename=None, output=None):
        """
        Download song from Datpiff

        Args:
            track (int,string) - name or index of song type(str or int)
            output (string) - location to save the song (optional)
            rename (string) - rename the song (optional)
                default will be song's name
        """
        selection = self.__index_of_song(track)
        if selection is None:
            return

        # Handles paths
        output = output or os.getcwd()
        if not Path.is_dir(output):
            raise FileNotFoundError("Invalid directory: %s" % output)

        song = self.songs[selection]

        # Handles song's renaming
        if rename:
            title = rename.strip() + ".mp3"
        else:
            title = " - ".join((self.artist, song.strip() + ".mp3"))

        title = Path.standardizeName(title)
        songname = Path.join(output, title)

        try:
            content = self._writeAudio(song).read()
            size = file_size(len(content))
            Path.writeFile(songname, content, mode="wb")
            screen.display_download_message(title, size)
        except:  # noqa: E722
            Verbose("Cannot download song %s" % songname)

    def downloadAlbum(self, output=None):
        """Download all tracks from Mixtape.

        Args:
            output ([type], optional): path to save mixtape.(default: current directory)
        """
        if not output:
            output = os.getcwd()
        elif not os.path.isdir(output):
            Verbose("Invalid directory: %s" % output)
            return

        formatted_title = " - ".join((self.artist, self.album))
        title = Path.standardizeName(formatted_title)
        filename = Path.join(output, title)

        # make a directory to store all the ablum's songs
        if not os.path.isdir(filename):
            os.mkdir(filename)
        ThreadQueue(self.download, self.songs, filename).execute()
        Verbose("\n%s %s saved" % (self.artist, self.album))
