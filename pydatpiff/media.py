import io
import os

from pydatpiff.utils.filehandler import File, Tmp
from pydatpiff.utils.utils import Object, Select, ThreadQueue, threader_wrapper

from .backend.audio.player import Player
from .backend.mediasetup import Album, Mp3
from .constants import verbose_message
from .errors import MediaError
from .frontend import screen
from .mixtapes import Mixtapes
from .urls import Urls
from .utils.request import Session

Verbose = screen.Verbose


class Media:
    """A media player that control the songs selected from Mixtapes"""

    player = None

    def __init__(self, mixtapes=None, pre_select=None, player="mpv", **kwargs):
        """
        Initialize a media player and load all mixtapes.

        Args:
            mixtapes (instance class) -- pydatpiff.Mixtapes instance (default: {None})
            pre_select (Integer,String) --  pre-selected mixtape's album, artist,or mixtapes.
                    See media.setMedia for more info (default: None - Optional)

        Raises:
            MediaError: Raises MediaError if mixtapes is not a subclass of pydatpiff.Mixtapes.
        """
        self.__setup(player)
        # Check if mixtape is valid
        self.__is_valid_mixtape(mixtapes)

        self._album_cover = None
        self.bio = None
        self._Mp3 = None
        self.url = None
        self.uploader = None
        self._session = Session()
        self.mixtapes = mixtapes
        self._artist_name = None
        self._album_name = None
        self._current_index = None
        self._selected_song = None
        self.__cache_storage = {}

        Verbose(verbose_message["MEDIA_INITIALIZED"])

        if pre_select:  # Run setMedia with argument here
            # This step is optional for users, but can save an extra setup
            # when selecting an album in setMedia.
            self.setMedia(pre_select)

    def __str__(self):
        album_name = self._album_name
        if album_name:
            return "{} Mixtape".format(album_name)
        return str(self.mixtapes)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.mixtapes.__class__)

    def __len__(self):
        try:
            return len(self.songs)
        except MediaError:
            Verbose(verbose_message["MEDIA_NOT_SET"])
            return 0

    def __setup(self, player=None):
        if not hasattr(self, "__temp_file"):
            Tmp.remove_temp_file_on_startup()
            self.__temp_file = Tmp.create()

        # Set the initial player. fallback to mpv if not specified
        self.player = Player.getPlayer(player)

    def _select(self, choice):
        """
        Queue and load  a mixtape to media player.
                            (See pydatpiff.media.Media.setMedia)

        :param: choice - (int) user selection by indexing an artist name or album name
                            (str)
        """
        # Map user selection according to the incoming datatype.
        # We map an integer to an artist and str to a mixtape.
        selection = None

        if isinstance(choice, int):
            # Adjust the selection to the correct index.
            total_mixtape = len(self.mixtapes)
            if choice >= total_mixtape:
                choice = total_mixtape
            selection = Select.get_leftmost_index(choice, options=self.mixtapes.artists)
        else:
            options = self.mixtapes.artists.copy()
            options.extend(self.mixtapes.mixtapes)

            selection = Select.get_index_of(choice, options=options)
        assert selection is not None, "Invalid selection"
        return selection

    def setMedia(self, mixtape):  # noqa
        """
        Initialize and set the Mixtape to Media Player.
        A pydatpiff.mixtapes.Mixtape's album will be load to the media player.

        Args:
            selection - pydatpiff.Mixtapes album's name or artist's name.
                int - will return the Datpiff.Mixtape artist at that index.
                str - will search for an artist from Mixtapes.artists (default)
                    or album from Mixtapes.album.

                See pydatpiff.mixtape.Mixtapes for a mixtape album or artist selection
        """

        # Mixtape's class will handle errors and None value

        mixtape_index = min(self._select(mixtape), len(self.mixtapes) - 1)

        # set Media's Mixtapes object attributes
        url = self.mixtapes._links[mixtape_index]  # noqa
        self.url = "".join((Urls.datpiff["base"], url))
        self.artist = self.mixtapes.artists[mixtape_index]
        self.album_cover = self.mixtapes.album_covers[mixtape_index]

        # set Media's Album detail attributes
        self.album = Album(url)
        self._Mp3 = Mp3(self.album)

        # get the album's uploader and bio
        self.uploader = getattr(self.album, "uploader", "unknown uploader")
        self.bio = getattr(self.album, "uploader", "no bio")
        formatted_title = " - ".join((self.artist, self.album.name))
        Verbose(verbose_message["MEDIA_SET"] % formatted_title)

    def __is_valid_mixtape(self, instance):
        """Verify media mixtape subclass is an instance of mixtapes' class

        Args:
            instance {instance class} -- Pydatpiff Mixtapes instance

        Returns:
            Boolean -- True or False if instance is subclass of pydatpiff Mixtape class
        """
        if not instance:
            raise MediaError(1)

        if not issubclass(instance.__class__, Mixtapes):
            raise MediaError(2, '"mixtape" must be Mixtapes object ')

    def find_song(self, name):
        """
         Search through all mixtapes songs and return all songs
         with song_name

        Args:
            song_name {str} -- song to search for.

        Returns:
            tuple -- returns a tuple containing mixtapes data (index,artist,album) from search.
        """

        # NOTE: Take a look at this video by James Powell
        # https://www.youtube.com/watch?v=R2ipPgrWypI&t=1748s at 55:00.

        song_name = Object.strip_and_lower(name)
        Verbose("\n" + verbose_message["SEARCH_SONG"] % song_name)
        links = self.mixtapes.links
        links = list(enumerate(links, start=1))
        results = ThreadQueue(Album.lookup_song, links).execute(song=song_name)
        if not results:
            Verbose(verbose_message["SONG_NOT_FOUND"] % song_name)
        results = Object.remove_list_null_value(results)
        return results

    def _index_of_song(self, select):
        """
        Parse all user input and return the correct song index.
        :param select: -  Media.songs name or index of Media.songs
               datatype: int: must be numerical
                         str: artist,mixtape, or song name
        """
        try:
            if isinstance(select, int):
                return Select.get_leftmost_index(select, self.songs)
            return Select.get_index_of(select, self.songs)
        except ValueError:
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
        if self._Mp3 is None:
            extra_message = '\nSet media by calling -->  Media.setMedia("album-name")'
            raise MediaError(3, extra_message)
        return self._Mp3.songs

    @property
    def mp3_urls(self):
        """Returns all parsed mp3 url"""
        return list(self._Mp3.mp3_urls)

    def show_songs(self):
        """Pretty way to Print all song names"""
        try:
            for index, song in enumerate(self.songs, start=1):
                Verbose("%s: %s" % (index, song))
        except MediaError:
            Verbose(verbose_message["MEDIA_NOT_SET"])

    @property
    def song(self):
        """Returns the current song set by user."""
        return self._selected_song

    @song.setter
    def song(self, name):
        """
        Set the current song to the song name or index.
        :param name: - song name or index of song
        """
        try:
            index = self._index_of_song(name)
            self._selected_song = self.songs[index]
            self._current_index = index
        except (ValueError, MediaError):
            Verbose(verbose_message["SONG_NOT_FOUND"] % name)

    def _cache_song(self, song, content):
        """
        Preserve the data from song and store it for future calls.
         This prevents calling the requests function again for the same song.
         Each data from a song will be stored in __cache_storage for future access.

        Args:
            song (str):  name of song
            content (byte): song's audio content
        """
        song = "-".join((self.artist, song))
        try:
            self.__cache_storage[song] = content
        except MemoryError:
            self.__cache_storage = {}

    def _retrieve_song_from_cache(self, song):
        """Retrieve song's audio content from cache
        Args:
            song (str): name of song

        Returns:
            Http response : A http response containing the song's audio contents.
        """
        requested_song = "-".join((self.artist, song))
        if requested_song in self.__cache_storage:
            return self.__cache_storage.get(requested_song)

    def _write_audio(self, track):
        """Write mp3 audio content to IO Bytes stream.
        Args:
            track (int,string): Name or index of song.

        Returns:
            BytesIO: A file-like API for reading and writing bytes objects.
        """

        try:
            selection = self._index_of_song(track)
            if selection is None:
                raise MediaError("Song not found")

            link = self.mp3_urls[selection]
            song_name = self.songs[selection]
            self._song_index = selection
        except:  # noqa
            return

        self.song = selection + 1

        # Retrieve song's content in cached
        response = self._retrieve_song_from_cache(song_name)
        if not response:
            response = self._session.method("GET", link)
            self._cache_song(song_name, response)

        return io.BytesIO(response.content)

    @property
    def autoplay(self):
        """Continuously play song from current mixtape album."""
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
        self._auto_play = auto  # noqa
        self._continuous_play()
        if auto:
            Verbose("\t----- AUTO PLAY ON -----")
        else:
            Verbose("\t----- AUTO PLAY OFF -----")

    @threader_wrapper
    def _continuous_play(self):
        """
        Automatically play each song from Album when autoplay is enable.
        """
        if self.autoplay:
            total_songs = len(self)
            if not self.song:
                Verbose(verbose_message["AUTO_PLAY_NO_SONG"])
                return

            track_number = self._index_of_song(self.song) + 2
            if track_number > total_songs:
                Verbose(verbose_message["AUTO_PLAY_LAST_SONG"])
                self.autoplay = False
                return

            while self.autoplay:
                current_track = self._index_of_song(self.song) + 1
                stopped = self.player._state.get("stopped")  # noqa
                if stopped:
                    next_track = current_track + 1

                    if next_track > total_songs:
                        Verbose(verbose_message["AUTO_PLAY_LAST_SONG"])
                        self.autoplay = False
                        break

                    Verbose(verbose_message["AUTO_PLAY_NEXT_SONG"])
                    self.play(next_track)
                    while self.player._state["stopped"]:  # noqa
                        pass

    def _get_audio_track(self, track):
        """
        Perform a lookup for song by its index or name and returns
        full track name and audio content.

        Args:   track (int,string): Name or index of song.
        Returns:    tuple: (track name, audio content)
        """
        if not track:
            Verbose("\n\t", verbose_message["NO_SONG_SELECTED"])
            raise MediaError(8, verbose_message["NO_SONG_SELECTED"])

        try:
            if isinstance(track, int):
                if track > len(self):
                    track = len(self)
            else:
                track = self._index_of_song(track) + 1
        except ValueError:  # ^ will throw ValueError if track  name is invalid
            Verbose(verbose_message["SONG_NOT_FOUND"] % track)
            raise MediaError(8, verbose_message["SONG_NOT_FOUND"] % track)

        content = self._write_audio(track).read()
        if not content:
            Verbose(verbose_message["UNAVAILABLE_SONG"])
            raise MediaError(9, verbose_message["UNAVAILABLE_SONG"])

        song_name = self.songs[self._song_index]
        return song_name, content

    def play(self, track=None, demo=False):
        """Play selected mixtape's track

        Args:
            track (int,string)- name or index of song.
            demo (bool, options) - True: demo buffer of song (default: False).
                False: play full song
        """

        if self.player is None:
            extended_msg = "Audio player is incompatible with device"
            raise MediaError(6, extended_msg)

        try:
            song_name, content = self._get_audio_track(track)
        except MediaError:
            return

        buffer_size = len(content)
        # play demo or full song
        if not demo:  # demo whole song
            chunk = content
            buffer = int(buffer_size)
        else:  # demo partial song
            buffer = int(buffer_size / 5)
            start = int(buffer / 5)
            chunk = content[start : buffer + start]
        size = File.get_human_readable_file_size(buffer)

        # write song to file
        File.write_to_file(self.__temp_file.name, chunk, mode="wb")

        # display message to user
        screen.display_play_message(self.artist, self.album, song_name, size, demo)

        song = " - ".join((self.artist, song_name))
        self.player.set_track(song, self.__temp_file.name)
        self.player.play  # noqa - play song is a property of the player class

    def download(self, track=None, rename=None, output=None):
        """
        Download song from Datpiff

        Args:
            track (int,string) - name or index of song type(str or int)
            output (string) - location to save the song (optional)
            rename (string) - rename the song (optional)
                default will be song's name
        """
        try:
            song, content = self._get_audio_track(track)
        except MediaError:
            return

        # Handles paths
        output = output or os.getcwd()
        if not File.is_dir(output):
            raise FileNotFoundError("Invalid directory: %s" % output)

        # Handles song's renaming
        if rename:
            song, _ = os.path.splitext(rename)
        title = " - ".join((self.artist, song.strip() + ".mp3"))

        file_name = File.standardize_file_name(title)
        file_name = File.join(output, file_name)

        size = File.get_human_readable_file_size(len(content))
        File.write_to_file(file_name, content, mode="wb")
        screen.display_download_message(title, size)

    def download_album(self, output=None):
        """Download all tracks from Mixtape.

        Args:
            output ([type], optional): path to save mixtape.(default: current directory)
        """
        if not output:
            output = os.getcwd()
        elif not os.path.isdir(output):
            Verbose(verbose_message["INVALID_DIRECTORY"] % output)
            return

        # must follow `download` method's arguments order
        ThreadQueue(
            self.download,
            self.songs,
        ).execute(rename=None, output=output)
        Verbose("\n" + verbose_message["SAVE_ALBUM"] % (self.artist + " " + self.album.name, output))
