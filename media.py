import os
import re
import math
import platform
import threading
import requests
import atexit
from functools import wraps
import tempfile
from .player import Player
from .mixtapes import Mixtapes

def converter(file_size):
    if file_size == 0:
        return '0B'
    
    size_name = ['B','KB','MB','GB','TB','PB','EB','ZB','YB']
    change = int(math.floor(math.log(file_size,1024)))
    power = math.pow(1024,change)
    result = round(file_size / power,2)
    return '%s %s'%(result,size_name[change])
 


class Media():
    """ Media player that control the songs selected from Mixtapes """ 
    def __new__(cls,*args,**kwargs):
        system = platform.system()
        if not hasattr(cls,'_tmpfile'):
            cls._tmpfile = tempfile.NamedTemporaryFile(delete=False)
            atexit.register(cls._remove_temp)
        return super(Media,cls).__new__(cls)

    def __str__(self):
        return "%s(%s('hot'))"%(self.__class__.__name__,self.mixtape.__name__)

    def __repr__(self):
        return 'Media(%s)'%(self.mixtape.__name__)


    def __init__(self, mixtape=None):
        """ Initialize Media 

        @@params: mixtape - Datpiff.Mixtapes object
        """
        print('Media initailize')
        if not mixtape:
            print('Mixtapes object must be pass to Media')
            raise ValueError()
        self._session = requests.Session()
        self.mixtape = mixtape
        self._artist_name = None
        self.album_name = None
        self.album_link = None
        self._song_index = None
        self._selected_song = None
        self.soup =None
        self._downloaded_song = None
        super(Media, self).__init__()

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
        choice = self.mixtape._select(selection)
        if not choice:
            print("Media is not set!\n-->\tIncorrect Value: %s" % selection)
            return
        self._artist_name = self.mixtape.artists[choice[1]]
        self.album_name = self.mixtape.mixtapes[choice[1]]
        self.album_link = "http://www.datpiff.com"+choice[0]
        self._getSongs()
        self._formatToHttps()
        print('Media set to %s - %s'%(self.artist,self.album))

        
    def _threader(f):
        """Threading wrapper function. """
        @wraps(f)
        def inner(self,*a,**kw):
            print('\nStart Threading')
            t= threading.Thread(target=f,args=(a,),kwargs=kw)
            t.daemon = True
            t.start()
            return t
        return inner

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


    @album.setter
    def album(self, name):
        self.setMedia(name)


    @property
    def songs(self):
        """ Return all album songs."""
        if hasattr(self,'_songs'):
            return self._songs


    def _getSongs(self):
        """ Collect all songs from current Mixtapes album.
            Do not use use Media.songs instead.
        """

        if not self.album_link:
            print("You have to set Media first ")
            return None

        web_link = "https://www.datpiff.com/" + self.album_link
        response = self._session.get(web_link)
        status = response.status_code
        if status != 200:
            print("No Media data available")
            return 
        text = response.text
        songs = re.findall(r'li[\s*].*title="(.*[\w\s]*)">',text)
        self._songs = songs
        return songs


    @property
    def show_songs(self):
        """Pretty way to display all song names"""
        try:
            songs = self.songs
            [print('%s: %s'%(a+1,b)) for a,b in enumerate(songs)]
        except TypeError:
            print("Please set Media first\nNo Artist name")

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
            self._selected_song =songs[index] 
            self._song_index  = index
        else:
            print('\n\t song was not found')


    @property
    def _song_link(self):
        """Current song album link"""
        if self._song_index is None:
            print('\n-- Media.song not set. Set "Media.song" to get mp3 link --')
            return None
        if hasattr(self,'_song_index'):
            return self._mp3_links[self._song_index]
        else:
            self._formatToHttps()

    @property
    def mp3urls(self):
        """Returns the parsed mp3 url"""
        return self._linksToUrls()


    def _formatToHttps(self): 
        """Get the raw mp3 link and convert them to https format""" 
        if not self.album_link:
            return
        response = self._session.get(self.album_link)
        if response.status_code == 200:
            text = response.text
            links = re.findall(r'meta\scontent\="(//[\w/?].*)"\sitemprop', text)
            if links:
                links = ['https:'+link for link in links]
                self._mp3_links = links # capturing as a variable 
                                        # to cache the response 
                return links
        else:
            print("\nBad album link:", self.album_link)


    def _linksToUrls(self,*args,**kwargs):
        """Parse mp3 links and convert them into Datpiff mp3 url format."""
        tid = self._mp3_links
        pd = [re.search(r'(d[\w.]*)/player/(m\w*)\?.*=(\d*)',link) for link in tid]
        urls =[]
        for part ,song in zip(pd,self.songs):
            song = re.sub('[^\w\s]','',song)
            data =  [part[1],part[2],part[3].zfill(2),re.sub(' ','%20',song)]
            urls.append('https://hw-mp3.{}/mixtapes/9/{}/{}%20-%20{}.mp3'.format(*data))
        return urls
        

    def _parseSelection(self,select):
        """Parse all user selection and return the correct songs
           @@params: select  - Media.songs name or index of Media.songs 
        """
        select = 1 if select == 0 else select
        songs = dict(enumerate(self.songs,start=1))
        selection = list(filter(lambda x: select in x \
                            or str(select).lower().strip() in x[1].lower(),
                            (songs.items())
                          ))
        if selection:
            return (min(selection)[0]) - 1
        else:
            print('\n\t -- No song was found --')


    def _cache(f):
        """
        _cache - Captures the songname and content when user play
         or download a song. This prevents downloading song content twice
         when playing or downloading a song. Data from each song will be 
         stored in _song_cache for future access.
        """
        @wraps(f)
        def inner(self,*args,**kwargs):
            if not hasattr(self,'_song_cache'):
                self._song_cache = {}
            fname = f.__name__
            data = f(self,*args,**kwargs)
            if data:
                name,response = data
                name = "-".join((self.artist,name))
                self._song_cache[name] = response
            return data
        return inner

    def _checkCache(self,song):
        """Check if song have already been download.
        If so,requests response is return.
        """
        in_cache = '-'.join((self.artist,song))
        if hasattr(self,'_song_cache'):
            if in_cache in self._song_cache:
                print('Grabbing %s from cache'%song)
                response  = self._song_cache[in_cache]
                return response
                

    @_cache
    def play(self, track=None, demo=False):
        """ 
        Play song (uses vlc media player) 
         @@params: track - name or index of song type(str or int)
         @@params: demo  - True: demo sample of song
                              False: play full song 
                              *default: False
        """
        selection = self._parseSelection(track)
        if selection is not None:
            link = self.mp3urls[selection]
            songname = self.songs[selection]
            
            # Write songname to file
            response = self._checkCache(songname)
            if response:
                content = response.content
            else:
                try:
                    # check if song already been downloaded 
                    response = self._session.get(link)
                    content = response.content
                    response.raise_for_status()
                except:
                    status = response.status_code
                    song = " - ".join((self.artist,songname))
                    print('\n%s song can not play. Try again '%(song))
                    return 

            track_size = len(content)
            # play demo or full song
            if not demo: # demo whole song
                chunk = content
                samp = int(track_size)
            else: # demo partial song
                samp = int(track_size/5)
                start = int(samp/5)
                chunk = content[start:samp+start]

            with open(self._tmpfile.name, "wb") as ws:
                ws.write(chunk)
            sorf = 'Demo' if demo else 'Full Song'
            print('\n%s %s %s'%('-'*20,sorf ,'-'*20))
            print('Song: %s - %s'%(self.artist,songname))
            print("Size:",converter(samp))
            if not hasattr(self,'player'):
                self.player = Player()
            self.player.play(self._tmpfile.name)
            return songname,response


    @_cache
    def download(self,track=False,output="" ,name=None):
        """
        Download song from Datpiff
        @@params: track - name or index of song type(str or int)
        @@output: location to save the song (optional)
        @@name:   rename the song (optional) default will be song's name 
        """
        selection = self._parseSelection(track)
        if selection is None:
            print('\n\t No song found to download')
            return 
        if os.path.isdir(output):
            location = output
        else:
            location = os.getcwd()
        link = self.mp3urls[selection]
        song = self.songs[selection]
        songname = '/'.join((location, self.artist + " - " + song.strip()+".mp3"))
        try:
            response = self._checkCache(song)
            if response:
                content = response.content
            else:
                response = self._session.get(link)
                response.raise_for_status()

            with open(songname, "wb") as ws:
                ws.write(response.content)
                print('\nSONGNAME: ',songname,
                        '\nSIZE:  ',converter(len(response.content)))
            return songname,response
        except:
                print("Error saving song Non-200 status")


    @_cache
    def downloadAlbum(self,location=None):
        if not location or  os.path.isdir(location):
                location = os.getcwd()
        
        fname = location + "\\"+self.artist + "-" + self.album
        fname = re.sub(' ','_',fname)
        #make a directory to store all the ablum's songs
        if not os.path.isdir(fname):
            os.mkdir(fname)

        for num, song in enumerate(self.songs):
            self.download(song,output=fname)
        print("\n%s %s saved" % (self.artist,self.album))

    @classmethod
    def _remove_temp(cls):
        try:
            cls.player.stop()
            cls._tmpfile.close()
            os.unlink(cls._tmpfile.name)
        except:
            print('temp file did not delete. %s'%cls._tmpfile)
        else:
            print('tmpfile deleted successfully')


