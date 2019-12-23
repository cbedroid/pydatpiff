import os
import io
import re
from .frontend.display import Print,Verbose
from .urls import Urls
from .player import Player
from .errors import MediaError
from .utils.request import Session
<<<<<<< HEAD:datpiff/media.py
from .backend.handler import converter,Tmp,Path
from .backend.mediasetup import Album,Mp3
=======
from .backend.filehandler import file_size,Tmp,Path
from .backend.mediasetup import Album,Mp3
from .backend.config import User,Datatype,Queued
<<<<<<< HEAD:datpiff/media.py
import traceback
>>>>>>> eca77c0... Refactor code, Change files name and method names in backup folder, Optimized speed of media.findSong function:pydatpiff/media.py
=======
>>>>>>> 9677925... implemented method for more mixtapes, Added backend/mixsetup.py:pydatpiff/media.py


class Media():
    """ Media player that control the songs selected from Mixtapes """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_tmpfile'):
            Tmp.removeTmpOnstart()
            cls._tmpfile = Tmp.create()
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
        songname = Datatype.strip_lowered(songname)
        links = self.mixtape.links
        links = list(enumerate(links,start=1))
        results = Queued(self._search,links,songname).run()
        if not results:
            Print('No song was found with this title ')
        results = Datatype.removeNone(results)
        return results
        """ 
        links = lists(enumerate(links,start=1))
        collector = []
        for index, link in enumerate(links,start=1):
            album = Album(link)
            name = album.name
            tracks = Mp3(album.embed_response).songs
            if any(songname in Datatype.strip_lowered(track) for track in tracks):
                collector.append((index,name)) 

        return collector
        """
        
    def _search(self,links,song):
        index,link = links
        album = Album(link)
        name = album.name
        tracks = Mp3(album.embed_response).songs
        if any(song in Datatype.strip_lowered(track) for track in tracks):
            return index,name 

       
        

    def setMedia(self, selection):
        """
        Setup and queues Datpiff.Mixtapes ablum to media player by selection 
        Datpiff.Mixtapes artists or album name.

        @@params: selection - Datpiff.Mixtapes album's name or artist's name.
            #datatype 
            int - will return the Datpiff.Mixtape artist at that index.
            str - will search for an artist from Mixtapes.artists (default)
                  or album from Mixtapes.ablum. 
        """
<<<<<<< HEAD:datpiff/media.py
        results = self.mixtape._select(selection)
        if not results:
=======
        result = self.mixtape._select(selection)
        if result is None:
            Verbose('SELECTION:',selection)
>>>>>>> eca77c0... Refactor code, Change files name and method names in backup folder, Optimized speed of media.findSong function:pydatpiff/media.py
            e_msg = '\n--> Mixtape "%s" was not found'%selection
            raise MediaError(1,e_msg)
        link,choice = results

<<<<<<< HEAD:datpiff/media.py
        self._artist_name = self.mixtape.artists[choice]
        self.album_name = self.mixtape.mixtapes[choice]
        self._setup(link)
        print('Setting Media to %s - %s' % (self.artist, self.album))
=======
        self._artist_name = self.mixtape.artists[result]
        self.album_name = self.mixtape.mixtapes[result]
        link = self.mixtape._links
        self._setup(link[result])
        
        Verbose('Setting Media to %s - %s' % (self.artist, self.album))
>>>>>>> eca77c0... Refactor code, Change files name and method names in backup folder, Optimized speed of media.findSong function:pydatpiff/media.py
        # only returning to check if choice was set
        return choice


    def _setup(self,link):
        self._album = Album(link)
        response = self._album.embed_response
        self._Mp3 = Mp3(response)
        self._song_cache = {}

       
    def _parseSelection(self, select):
        """
        Parse all user selection and return the correct songs

        @@params: select  - Media.songs name or index of Media.songs 
        """
<<<<<<< HEAD:datpiff/media.py
        select = 1 if select == 0 else select
        songs = dict(enumerate(self.songs, start=1))

        # checking from index 
        if isinstance(select,int):
            length = len(self.songs) + 1
            if select >= 0 and select < length:
                select = 1 if select == 0 else select
                return select-1

        select = str(select).lower().strip()
        selection = list(filter(lambda x: select in x[1].lower(),(songs.items()
                            )))

        if selection:
            return (min(selection)[0]) - 1
        else:
            print('\n\t -- No song was found --')
=======
        try:
            return User.selection(select,self.songs,[x.lower() for x in self.songs])
        except MediaError as e:
            raise MediaError(5)

>>>>>>> eca77c0... Refactor code, Change files name and method names in backup folder, Optimized speed of media.findSong function:pydatpiff/media.py


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


    @property
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
        index = self._parseSelection(name)
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

        selection = self._parseSelection(track)
        if selection is None:
            return 

        self._song_index = selection
        link = self.mp3urls[selection]
        songname = self.songs[selection]
        self.song= selection + 1

        # Write songname to file
        # check if song has been already downloaded 
        # if so then get the response from cache
        response = self._checkCache(songname)
        if not response:
            response = self._session.method('GET', link)
            self._cacheSong(songname, response)

        return io.BytesIO(response.content)


    def play(self, track=None, demo=False):
        """ 
        Play song (uses vlc media player) 

         @@params: track - name or index of song type(str or int)
         @@params: demo  - True: demo sample of song
                              False: play full song 
                              *default: False
        """
        if track is None:
            Print('\n\t -- No song was entered --')
            return 

        if isinstance(track,int):
            if track > len(self):
                raise MediaError(4) 

        try
            content = self.mp3Content(track).read()
<<<<<<< HEAD:datpiff/media.py
        except:
            print('\n\t-- No song was found --')
=======
        except Exception:
            Print('\n\t-- No song was found --')
>>>>>>> eca77c0... Refactor code, Change files name and method names in backup folder, Optimized speed of media.findSong function:pydatpiff/media.py
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
        if not hasattr(self, 'player'):
            self.player = Player()
        
        self.player.setTrack(song,self._tmpfile.name)
        self.player.play


    def download(self, track=False, output="", name=None):
        """
        Download song from Datpiff

        @@params: track - name or index of song type(str or int)
        @@output: location to save the song (optional)
        @@name:   rename the song (optional)
            default will be song's name 
        """
        selection = self._parseSelection(track)
        if selection is None:
            return

        output = output or os.getcwd()
        if not Path.is_dir(output):
            Print('Invalid directory: %s'%output)
            return 

        link = self.mp3urls[selection]
        song = self.songs[selection]
        title  = ' - '.join(( self.artist,song.strip()+".mp3" ))
        title = Path.toStandard(title)
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
        title = Path.toStandard(title)
        fname = Path.join(output,title) 
        
        # make a directory to store all the ablum's songs
        if not os.path.isdir(fname):
            os.mkdir(fname)

        for num, song in enumerate(self.songs):
            self.download(song, output=fname)
        Print("\n%s %s saved" % (self.artist, self.album))

