import os
import io
from .frontend.display import Print,Verbose
from .urls import Urls
from .errors import MediaError
from .utils.request import Session
from .backend.filehandler import file_size,Tmp,Path
from .backend.mediasetup import Album,Mp3
from .backend.config import User,Datatype,Queued,Threader
from .backend.audio.player import Player
import traceback

#TODO NOT finish writig baseplayer method and subclasses
#   from .backend.audio.player import BasePlayer as player 
#   will cahnge import to another name
#    change name of player 


class Media():
    """ Media player that control the songs selected from Mixtapes """
    
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_tmpfile'):
            Tmp.removeTmpOnstart()
            cls._tmpfile = Tmp.create()

        if not hasattr(cls,'player'):
            try:
                cls.player = Player.getPlayer()
            except Exception as e:
                cls.player = None

            if cls.player is None: # Incase user reinitalize Media class
                raise MediaError(7)

        return super(Media, cls).__new__(cls)


    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self.mixtape)


    def __repr__(self):
        return 'Media(%s)' % (self.mixtape)


    def __len__(self):
        if hasattr(self,'songs'):
            return len(self.songs)
        else:
            return 0

    def __init__(self, mixtape=None):
        """ Initialize Media 

        @@params: mixtape - Datpiff.Mixtapes object
        """
        if 'mixtapes.Mixtapes' not in str(type(mixtape)):
            raise MediaError(2,'must pass a mixtape object to Media class')

        Verbose('Media initialized')
        if not mixtape:
            raise MediaError(1)

        self._session = Session()
        self.mixtape = mixtape
        self._artist_name = None
        self.album_name = None
        self._current_index = None
        self._selected_song = None
        self._downloaded_song = None
        super(Media, self).__init__()

     
    def findSong(self,songname):
        """
        Search through all mixtapes songs and return all songs 
        with songname

        :param: songname - name of the song to search for
        """
        
        #TODO:look this video with James Powell
        # https://www.youtube.com/watch?v=R2ipPgrWypI&t=1748s at 55:00.
        # Implement a generate function , so user dont have to wait on all the results at once 
        # Also thread this main function, to unblock user from still using program while 
        # it wait for result to be finished.
        songname = Datatype.strip_lowered(songname)
        links = self.mixtape.links
        links = list(enumerate(links,start=1))
        results = Queued(self._searchAlbumsFor,links).run(songname)
        if not results:
            Print('No song was found with this title ')
        results = Datatype.removeNone(results)
        return results

        
    def _searchAlbumsFor(self,links,song):
        """
        Search through all Albums and return all Albums
        that contains similiar songs' title.
        :param: song: title of the song to search for
        """
        index,link = links
        album = Album(link)
        name = album.name
        tracks = Mp3(album.embed_response).songs
        if any(song in Datatype.strip_lowered(track) for track in tracks):
            return index,name 


    def setMedia(self, selection):
        """
        Initialize and set the an Album to Media Player.
        A pydatpiff.Mixtape's ablum will be load to the media player.

        :params: selection - pydatpiff.Mixtapes album's name or artist's name.
            int - will return the Datpiff.Mixtape artist at that index.
            str - will search for an artist from Mixtapes.artists (default)
                  or album from Mixtapes.ablum. 

            note: see pydatpiff.Mixtapes for album or artist selection 
        """

        result = self.mixtape._select(selection)
        if result is None:
            Verbose('SELECTION:',selection)
            e_msg = '\n--> Mixtape "%s" was not found'%selection
            raise MediaError(1)

        # set up all Album's Info
        self._artist_name = self.mixtape.artists[result]
        self.album_name = self.mixtape.mixtapes[result]
        link = self.mixtape._links

        self._loadAlbum(link[result])
        Verbose('Setting Media to %s - %s' % (self.artist, self.album))


    def _loadAlbum(self,link):
        self._album = Album(link)
        response = self._album.embed_response
        self._Mp3 = Mp3(response)
        self._song_cache = {}

       
    def _getIndexOf(self, select):
        """
        Parse all user input and return the correct song index.
        :param select: -  Media.songs name or index of Media.songs 
               datatype: int: must be numerical
                         str: artist,mixtape, or song name
        """
        try:
            return User.selection(select,self.songs,[x.lower() for x in self.songs])
        except MediaError as e:
            raise MediaError(5)


    @property
    def artist(self):
        """Return the current artist name."""
        return self._artist_name


    @artist.setter
    def artist(self, name):
        """Set the current artist name."""
        self.setMedia(name)


    @property
    def album(self):
        """Return the current album name."""
        return self.album_name
        return Album.name


    @album.setter
    def album(self, name):
        self.setMedia(name)


    @property
    def songs(self):
        """ Return all album songs."""
        if not hasattr(self,'_Mp3'):
            e_msg = 'Set media by calling -->  Media.setMedia("Album name")'
            raise MediaError(3,e_msg)
        return self._Mp3.songs


    @property
    def mp3urls(self):
        """Returns the parsed mp3 url"""
        return list(self._Mp3.mp3Urls)


    def show_songs(self):
        """Pretty way to Print all song names"""
        try:
            songs = self.songs
            [Print('%s: %s' % (a+1, b)) for a, b in enumerate(songs)]
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

        @@params: name  - Media.songs name or index of Media.songs 
        """
        songs = self.songs
        index = self._getIndexOf(name)
        if index is not None:
            self._selected_song = songs[index]
            self._current_index = index
        else:
            Print('\n\t song was not found')


    def _cacheSong(self, song, data):
        """
        _cacheSong - Captures the songname and content when user play
         or download a song. This prevents downloading song content twice
         when playing or downloading a song. Data from each song will be 
         stored in _song_cache for future access.
        """
        name = "-".join((self.artist, song))
        try:
            self._song_cache[name] = data
        except MemoryError:
            self._song_cache = {}



    def _checkCache(self, song):
        """Check if song have already been download.
        If so,requests response is return.
        """
        in_cache = '-'.join((self.artist, song))
        if hasattr(self, '_song_cache'):
            if in_cache in self._song_cache:
                response = self._song_cache[in_cache]
                return response


    def mp3Content(self,track):
        """
        Return content of the song in IO Bytes object

        @@params: track - name or track index of song   
        """

        selection = self._getIndexOf(track)
        if selection is None:
            return 

        self._song_index = selection
        link = self.mp3urls[selection]
        songname = self.songs[selection]
        self.song = selection + 1

        # Write songname to file
        # check if song has been already downloaded 
        # if so then get the response from cache
        response = self._checkCache(songname)
        if not response:
            response = self._session.method('GET', link)
            self._cacheSong(songname, response)

        return io.BytesIO(response.content)

    @property
    def autoplay(self):
        ''' Continuous play song from current album'''
        if hasattr(self,'_auto_play'):
            return self._auto_play

    @autoplay.setter
    def autoplay(self,auto=False):
        self._auto_play = auto
        self._continousPlay()
        if auto:
            Verbose('SETTING AUTO PLAY ON')
        else:
            Verbose('SETTING AUTO PLAY OFF')


    @Threader
    def _continousPlay(self):
         if self.autoplay:
            total_song = len(self)
            current_song =  self.song
            if not current_song:
                Verbose('Must play a song before setting autoplay')
                return 

            current_track = self._getIndexOf(current_song)+1
            while current_track < len(self) and self.autoplay:
                state = self.player._state.get('playing')
                next_track = current_track + 1
                if not state:
                    Verbose('Loading next track')
                    if next_track > len(self):
                        Verbose('AUTO PLAY OFF')
                        self.autoplay = False
                        break
                    Verbose('AUTO PLAY ON')
                    self.play(next_track)
                    current_track = next_track
            
    def play(self, track=None, demo=False):
        """ 
        Play song (uses vlc media player) 

         @@params: track - name or index of song type(str or int)
         @@params: demo  - True: demo sample of song
                              False: play full song 
                              *default: False
        """
        if self.player is None:
            extented_msg = 'Audio player is incompatible with device'
            raise MediaError(6,extented_msg)
            return 

        if track is None:
            Print('\n\t -- No song was entered --')
            return 

        if isinstance(track,int):
            if track > len(self):
                raise MediaError(4) 

        try:
            content = self.mp3Content(track).read()
        except Exception:
            Print('\n\t-- No song was found --')
            return 

        songname = self.songs[self._song_index]
        track_size = len(content)
        # play demo or full song
        if not demo:  # demo whole song
            chunk = content
            samp = int(track_size)
        else:  # demo partial song
            samp = int(track_size/5)
            start = int(samp/5)
            chunk = content[start:samp+start]

        with open(self._tmpfile.name, "wb") as ws:
            ws.write(chunk)
        sorf = 'Demo' if demo else 'Full Song'
        Verbose('\n%s %s %s' % ('-'*20, sorf, '-'*20))
        Verbose('Song: %s - %s' % (self.artist, songname))
        Verbose("Size:", file_size(samp))
        song = " - ".join((self.artist, songname))
        self.player.setTrack(song,self._tmpfile.name)
        self.player.play
        
        

    def download(self, track=False, output="", rename=None):
        """
        Download song from Datpiff

        @@params: track - name or index of song type(str or int)
        @@output: location to save the song (optional)
        @@rename:   rename the song (optional)
            default will be song's name 
        """
        selection = self._getIndexOf(track)
        if selection is None:
            return
        
        #Handles paths
        output = output or os.getcwd()
        if not Path.is_dir(output):
            Print('Invalid directory: %s'%output)
            return 
        link = self.mp3urls[selection]
        song = self.songs[selection]
        
        #Handles song's naming 
        if rename:
            title  = rename.strip() + ".mp3" 
        else:
            title  = ' - '.join(( self.artist,song.strip()+".mp3" ))
        title = Path.standardizeName(title)
        songname = Path.join(output,title)

        try:
            response = self._checkCache(song)
            if response:
                content = response.content
            else:
                response = self._session.method('GET', link)
                response.raise_for_status()

            with open(songname, "wb") as ws:
                ws.write(response.content)
                Verbose('\nSONGNAME: ', songname,
                               '\nSIZE:  ', file_size(len(response.content)))
            self._cacheSong(songname, response)
        except:
            Print('Cannot download song %s' % songname)


    def downloadAlbum(self, output=None):
        if not output:
            output = os.getcwd()
        elif not os.path.isdir(output):
            Print('Invalid directory: %s'%output)
            return

        title = "-".join((self.artist, self.album))
        title = Path.standardizeName(title)
        fname = Path.join(output,title) 
        
        # make a directory to store all the ablum's songs
        if not os.path.isdir(fname):
            os.mkdir(fname)

        for num, song in enumerate(self.songs):
            self.download(song, output=fname)
        Queued(self.download,song,fname).run()
        Print("\n%s %s saved" % (self.artist, self.album))

