import os
import io
from .urls import Urls
from .errors import MediaError, InstallationError
from .utils.request import Session
from .backend.audio.player import Player
from .backend.mediasetup import Album, Mp3
from .frontend.display import Print, Verbose, Show
from .backend.filehandler import file_size, Tmp, Path
from .backend.config import User, Datatype, Queued, Threader
from .mixtapes import Mixtapes

# TODO NOT finish writig baseplayer method and subclasses
#   from .backend.audio.player import BasePlayer as player
#   will cahnge import to another name
#    change name of player


class Media:
    """ Media player that control the songs selected from Mixtapes """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "__tmpfile"):
            Tmp.removeTmpOnstart()
            cls.__tmpfile = Tmp.create()

        if hasattr(cls, "player"):
            if kwargs.get("player"):
                cls.player = Player.getPlayer(**kwargs)

        elif not hasattr(cls, "player"):
            try:
                cls.player = Player.getPlayer(**kwargs)
            except Exception as e:
                cls.player = None

        if cls.player is None:  # Incase user reinitalize Media class
            raise MediaError(7, InstallationError._extra)

        return super(Media, cls).__new__(cls)

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self._Mixtapes)

    def __repr__(self):
        return "Media(%s)" % (self._Mixtapes)

    def __len__(self):
        if hasattr(self, "songs"):
            return len(self.songs)
        else:
            return 0

    def __init__(self, mixtape=None, **kwargs):
        """ 
        Initialize Media and load all mixtapes.

        :param: mixtape - Datpiff.Mixtapes object
        """
        if not self.__isMixtapesObject(mixtape):
            raise MediaError(2, "must pass a mixtape object to Media class")

        Verbose("Media initialized")
        if not mixtape:
            raise MediaError(1)

        self._session = Session()
        self._Mixtapes = mixtape
        self._artist_name = None
        self._album_name = None
        self._current_index = None
        self._selected_song = None
        self.__downloaded_song = None
        super(Media, self).__init__()

    def __isMixtapesObject(self, obj):
        try:
            if issubclass(obj.__class__, Mixtapes):
                return True
        except:
            pass
        return False

    def findSong(self, songname):
        """
        Search through all mixtapes songs and return all songs 
        with songname

        :param: songname - name of the song to search for
        """

        # TODO:look this video with James Powell
        # https://www.youtube.com/watch?v=R2ipPgrWypI&t=1748s at 55:00.
        # Implement a generator function , so user dont have to wait on all the results at once
        # Also thread this main function, to unblock user from still using program while
        # it wait for result to be finished.
        songname = Datatype.strip_lowered(songname)
        Print("\nSearching for song: %s ..." % songname)
        links = self._Mixtapes.links
        links = list(enumerate(links, start=1))
        results = Queued(self.__searchAlbumFor, links).run(songname)
        if not results:
            Print("No song was found with the name: %s " % songname)
        results = Datatype.removeNone(results)
        return results

    def __searchAlbumFor(self, links, song, *args, **kwargs):
        """
        Search through all Albums and return all Albums
        that contains similiar songs' title.

        :param: song - title of the song to search for
        :param: links - all mixtapes links
        """
        index, link = links
        album = Album(link)
        name = album.name
        tracks = Mp3(album.datpiff_player_response).songs
        for track in tracks:
            if song in Datatype.strip_lowered(track):
                return {"ablumNo": index, "album": name, "song": track}

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

        result = self._Mixtapes._select(selection)
        if result is None:
            Verbose("SELECTION:", selection)
            e_msg = '\n--> Mixtape "%s" was not found' % selection
            raise MediaError(1)

        # set up all Album's Info
        max_result = len(self._Mixtapes) - 1
        result = result if result <= max_result else max_result
        self._artist_name = self._Mixtapes.artists[result]
        self._album_name = self._Mixtapes.mixtapes[result]
        self._album_cover = self._Mixtapes.album_covers[result]

        link = self._Mixtapes._links

        self.__setupMedia(link[result])
        Verbose("Setting Media to %s - %s" % (self.artist, self.album))

    def __setupMedia(self, link):
        """
        Initial an Album and sets all Mp3 songs'tags
        
        param: link - Album's mixtape link
        """
        album = Album(link)
        self._Mp3 = Mp3(album.datpiff_player_response)
        # get the ablum's uploader
        self.uploader = album.uploader
        # get ablum bio
        self.bio = album.bio
        self.__cache_storage = {}

    def __index_of_song(self, select):
        """
        Parse all user input and return the correct song index.
        :param select: -  Media.songs name or index of Media.songs 
               datatype: int: must be numerical
                         str: artist,mixtape, or song name
        """
        try:
            return User.selection(select, self.songs, [x.lower() for x in self.songs])
        except MediaError as e:
            raise MediaError(5)

    @property
    def artist(self):
        """Return the current artist name."""
        return self._artist_name

    @artist.setter
    def artist(self, name):
        self.setMedia(name)

    @property
    def album(self):
        """Return the current album name."""
        return self._album_name

    @album.setter
    def album(self, name):
        self.setMedia(name)

    @property
    def album_cover(self):
        if hasattr(self, "_album_cover"):
            return self._album_cover
        return ""

    @album_cover.setter
    def album_cover(self, url):
        self._album_cover = url

    @property
    def songs(self):
        """ Return all songs from album."""
        if not hasattr(self, "_Mp3"):
            e_msg = '\nSet media by calling -->  Media.setMedia("Album name")'
            raise MediaError(3, e_msg)
        return self._Mp3.songs

    @property
    def __mp3urls(self):
        """Returns all parsed mp3 url"""
        return list(self._Mp3.mp3Urls)

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
        link = self.__mp3urls[selection]
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
        Show.mediaPlayMsg(self.artist, songname, size, demo)

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
        link = self.__mp3urls[selection]
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
            if response:
                content = response.content
            else:
                response = self._session.method("GET", link)
                response.raise_for_status()

            size = file_size(len(response.content))
            Path.writeFile(songname, response.content, mode="wb")
            Show.mediaDownloadMsg(title, size)
            self._cacheSong(songname, response)
        except:
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
