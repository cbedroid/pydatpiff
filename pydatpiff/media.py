import io
import os

from .backend.audio.player import Player
from .backend.filehandler import Path, Tmp, file_size
from .backend.mediasetup import Album, Mp3
from .backend.utils import Object, Queued, Selector, Threader
from .errors import InstallationError, MediaError
from .frontend.display import Print, Show, Verbose
from .mixtapes import Mixtapes
from .urls import Urls
from .utils.request import Session


class Media:
    """Media player that control the songs selected from Mixtapes"""

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "__tmpfile"):
            Tmp.removeTmpOnStart()
            cls.__tmpfile = Tmp.create()

        player = kwargs.get("player", None)
        # Ths point here is to keep player global
        # redefining player here, the user will have to update
        # player locally in program themselves.
        # NOTE: Need to find an effecient way to update
        # player both in program and globally.

        if hasattr(cls, "player") and player:
            # if player is redfined
            # Updated player. Effective only if user changes baseplayer
            # Ex: changing MPV to VLC ..etc ...vice versa
            cls.player = Player.getPlayer(**kwargs)

        elif not hasattr(cls, "player"):
            try:
                cls.player = Player.getPlayer(**kwargs)
            except:  # noqa: E722
                cls.player = None

        if cls.player is None and not hasattr(cls, "player"):
            raise MediaError(7, InstallationError._extra)

        return super(Media, cls).__new__(cls)

    def __str__(self):
        album_name = self._album_name
        if album_name:
            return "{} Mixtape".format(album_name)
        return str(self._Mixtapes)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self._Mixtapes.__class__)

    def __len__(self):
        if hasattr(self, "songs"):
            return len(self.songs)
        else:
            return 0

    def __init__(self, mixtape=None, pre_selection=None, **kwargs):
        """
        Initialize Media and load all mixtapes.

        Keyword Arguments:
            mixtape {instance class} -- pydatpiff.Mixtapes class instance (default: {None})
            pre_selection {Integer,String} --  pre-selected mixtape's ablum,artist,or mixtapes.
                    See media.SetMedia for more info (default: None - Optional)

        Raises:
            MediaError: Raises MediaError if mixtapes is not an subclass of pydatpiff.Mixtapes.
        """
        self._session = Session()
        self._Mixtapes = mixtape
        self._artist_name = None
        self._album_name = None
        self._current_index = None
        self._selected_song = None
        self.__downloaded_song = None

        # Check if mixtape is valid
        self.__isMixtapesObject(mixtape)

        Verbose("Media initialized")

        if pre_selection:  # Run setMedia with argument here
            # This step is optional for users, but can save an extra setp
            # when selecting an album in setMedia.
            self.setMedia(pre_selection)

    def setMedia(self, selection):
        """
        Initialize and set the an Album to Media Player.
        A pydatpiff.mixtapes.Mixtape's ablum will be load to the media player.

        :param: selection - pydatpiff.Mixtapes album's name or artist's name.
            int - will return the Datpiff.Mixtape artist at that index.
            str - will search for an artist from Mixtapes.artists (default)
                  or album from Mixtapes.ablum.

            note: see pydatpiff.mixtape.Mixtapes for album or artist selection
        """

        # Mixtape's class will handle errors and None value

        mixtape_index = self._Mixtapes._select(selection)

        # set up all Album's Info
        total_mixtape = len(self._Mixtapes) - 1
        if mixtape_index > total_mixtape:
            mixtape_index = total_mixtape

        self.artist = self._Mixtapes.artists[mixtape_index]
        # self.album = self._Mixtapes.mixtapes[mixtape_index]
        self.album_cover = self._Mixtapes.album_covers[mixtape_index]

        url = self._Mixtapes._links[mixtape_index]
        self.url = "".join((Urls.datpiff["base"], url))
        self.album = Album(url)
        self._Mp3 = Mp3(self.album)

        # get the album's uploader
        self.uploader = self.album.uploader
        # get album bio
        self.bio = self.album.bio
        self.__cache_storage = {}
        Verbose("Setting Media to %s - %s" % (self.artist, self.album))

    def __isMixtapesObject(self, instance):
        """Verify subclass is an instance of mixtapes' class

        Arguments:
            instance {instance class} -- pydatpiff's Mixtapes instance

        Returns:
            Boolean -- True or False if instance is subclass of pydatpiff Mixtape class
        """
        if not instance:
            raise MediaError(1)

        if not issubclass(instance.__class__, Mixtapes):
            raise MediaError(2, "must pass a mixtape object to Media class")

    def findSong(self, songname):
        """
         Search through all mixtapes songs and return all songs
         with songname

        Arguments:
            songname {Str} -- song to search for.

        Returns:
            tuple -- returns a tuple containing mixtapes data (index,artist,album) from search.
        """

        # TODO:look this video with James Powell
        # https://www.youtube.com/watch?v=R2ipPgrWypI&t=1748s at 55:00.
        # Implement a generator function , so user dont have to wait on all the results at once
        # Also thread this main function, to unblock user from still using program while
        # it wait for result to be finished.
        songname = Object.strip_and_lower(songname)
        Print("\nSearching for song: %s ..." % songname)
        links = self._Mixtapes.links
        links = list(enumerate(links, start=1))
        results = Queued(Album.searchFor, links).run(songname)
        if not results:
            Print("No song was found with the name: %s " % songname)
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
                return Selector.select_from_index(select, self.songs)
            return Selector.select_from_choices(select, self.songs)
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
            self._album_cover = None
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
            [Print("%s: %s" % (a + 1, b)) for a, b in enumerate(songs)]
        except TypeError:
            Print("Please set Media first\nNo Artist name")

    @property
    def song(self):
        """Returns the current song set by user."""
        return self._selected_song

    @song.setter
    def song(self, name):
        """
        Set current song
        :param: name - name of song or song's index
        """
        songs = self.songs
        index = self.__index_of_song(name)
        if index is not None:
            self._selected_song = songs[index]
            self._current_index = index
        else:
            Print("\n\t song was not found")

    def _cacheSong(self, song, content):
        """
         Preserve the data from song and store it for future calls.
         This prevents calling the requests function again for the same song.
         Each data from a song will be stored in __cache_storage for future access.

        :param: song - name of the song
        :param: content - song content
        """
        name = "-".join((self.artist, song))
        try:
            self.__cache_storage[name] = content
        except MemoryError:
            self.__cache_storage = {}

    def _checkCache(self, songname):
        """
        Check whether song has been download already.

        :param:

        """
        requested_song = "-".join((self.artist, songname))
        if hasattr(self, "__cache_storage"):
            if requested_song in self.__cache_storage:
                response = self.__cache_storage.get(requested_song)
                if not response:
                    extended_msg = "%s not in cache_storage" % songname
                    raise MediaError(8, extended_msg)
                return response

    def _getMp3Content(self, track):
        """
        Return content of the song in IO Bytes object

        :param: track - name of song  or song index
        """

        selection = self.__index_of_song(track)
        if selection is None:
            return

        self.__song_index = selection
        link = self.mp3_urls[selection]
        songname = self.songs[selection]
        self.song = selection + 1

        # Write songname to file
        # check if song has been already downloaded
        # if so then get the response from cache
        response = self._checkCache(songname)
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
        """
         Sets the autoplay function.

        :param: auto - disable or enable autoplay
                 datatype: boolean
                 default: False
        """
        self._auto_play = auto
        self._continousPlay()
        if auto:
            Verbose("\t----- AUTO PLAY ON -----")
        else:
            Verbose("\t----- AUTO PLAY OFF -----")

    @Threader
    def _continousPlay(self):
        """
        Automatically play each song from Album when autoplay is enable.
        """
        if self.autoplay:
            total_songs = len(self)
            if not self.song:
                Verbose("Must play a song before setting autoplay")
                return

            trackno = self.__index_of_song(self.song) + 2
            if trackno > total_songs:
                Print("AutoPlayError: Current track is the last track")
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
        """
        Play song (uses vlc media player)

         :param: track - name or index of song type(str or int)
         :param: demo  - True: demo sample of song
                              False: play full song
                              *default: False
        """
        if self.player is None:
            extented_msg = "Audio player is incompatible with device"
            raise MediaError(6, extented_msg)

        if track is None:
            Print("\n\t -- No song was entered --")
            return

        if isinstance(track, int):
            if track > len(self):
                raise MediaError(4)

        try:
            content = self._getMp3Content(track).read()
        except Exception:
            Print("\n\t-- No song was found --")
            return

        songname = self.songs[self.__song_index]
        track_size = len(content)
        # play demo or full song
        if not demo:  # demo whole song
            chunk = content
            samp = int(track_size)
        else:  # demo partial song
            samp = int(track_size / 5)
            start = int(samp / 5)
            chunk = content[start : samp + start]
        size = file_size(samp)

        # write song to file
        Path.writeFile(self.__tmpfile.name, chunk, mode="wb")

        # display message to user
        Show.mediaPlayMsg(self.artist, self.album, songname, size, demo)

        song = " - ".join((self.artist, songname))
        self.player.setTrack(song, self.__tmpfile.name)
        self.player.play

    def download(self, track=False, output="", rename=None):
        """
        Download song from Datpiff

        :param: track - name or index of song type(str or int)
        :param: output - location to save the song (optional)
        :param: rename - rename the song (optional)
                default will be song's name
        """
        selection = self.__index_of_song(track)
        if selection is None:
            return

        # Handles paths
        output = output or os.getcwd()
        if not Path.is_dir(output):
            Print("Invalid directory: %s" % output)
            return
        link = self.mp3_urls[selection]
        song = self.songs[selection]

        # Handles song's naming
        if rename:
            title = rename.strip() + ".mp3"
        else:
            title = " - ".join((self.artist, song.strip() + ".mp3"))
        title = Path.standardizeName(title)
        songname = Path.join(output, title)

        try:
            response = self._checkCache(song)
            if response is None:
                response = self._session.method("GET", link)
                response.raise_for_status()

            size = file_size(len(response.content))
            Path.writeFile(songname, response.content, mode="wb")
            Show.mediaDownloadMsg(title, size)
            self._cacheSong(songname, response)
        except:  # noqa: E722
            Print("Cannot download song %s" % songname)

    def downloadAlbum(self, output=None):
        """
        Download the full ablum.

        :param: output - directory to save album
                :default - current directory
        """
        if not output:
            output = os.getcwd()
        elif not os.path.isdir(output):
            Print("Invalid directory: %s" % output)
            return

        title = "-".join((self.artist, self.album))
        title = Path.standardizeName(title)
        fname = Path.join(output, title)

        # make a directory to store all the ablum's songs
        if not os.path.isdir(fname):
            os.mkdir(fname)
        Queued(self.download, self.songs, fname).run()
        Print("\n%s %s saved" % (self.artist, self.album))
