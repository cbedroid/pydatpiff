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
        self._title_name = None
        self.album_link = None
        self._song_index = None
        self._selected_song = None
        self.soup =None
        self._downloaded_song = None
        self._song_cache = {}
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
        self._title_name = self.mixtape.titles[choice[1]]
        self.album_link = "http://www.datpiff.com"+choice[0]
        self._get_songs()
        self._player_links()

        
    def _threader(f):
        @wraps(f)
        def inner(self,*a,**kw):
            print('\nStart Threading')
            fun = f(self,*a,**kw)
            t= threading.Thread(target=funct,args=(a,),kwargs=kw)
            t.daemon = True
            t.start()
            return t
        return inner

    @property
    def artist(self):
        return self._artist_name


    @artist.setter
    def artist(self, name):
        self.setMedia(name)


    @property
    def title(self):
        return self._title_name


    @title.setter
    def title(self, name):
        self.setMedia(name)


    @property
    def songs(self):
        """ All albums songs."""
        if hasattr(self,'_songs'):
            return self._songs


    def _get_songs(self):
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
        try:
            songs = self.songs
            [print('%s: %s'%(a+1,b)) for a,b in enumerate(songs)]
        except TypeError:
            print("Please set Media first\nNo Artist name")

    @property
    def song(self):
        return self._selected_song

    @song.setter
    def song(self, name):
        songs = self.songs
        index = self._parse_selection(name)
        if index is not None:
            self._selected_song =songs[index] 
            self._song_index  = index
        else:
            print('\n\t song was not found')

    @property
    def _song_link(self):
        if self._song_index is None:
            print('\n-- Media.song not set. Set "Media.song" to get mp3 link --')
            return None
        return self.mp3Links[self._song_index]

    @property
    def mp3Urls(self):
        return self._make_mp3_url()

    @property
    def mp3Links(self):
        if hasattr(self,'_mp3_links'):
            return self._mp3_links

    @mp3Links.setter
    def mp3Links(self,*args):
        self._player_links()

    def _player_links(self, path=None):
        """Get the raw mp3 link and convert them to https format""" 
        if not self.album_link:
            return
        response = self._session.get(self.album_link)
        if response.status_code == 200:
            text = response.text
            links = re.findall(r'meta\scontent\="(//[\w/?].*)"\sitemprop', text)
            if links:
                links = ['https:'+link for link in links]
                self._mp3_links = links
                return links
        else:
            print("\nBad album link:", self.album_link)


    def _make_mp3_url(self,*args,**kwargs):
        #track=None,index = None):
        #def buildlink(self)

        tid = self.mp3Links
        pd = [re.search(r'(d[\w.]*)/player/(m\w*)\?.*=(\d*)',link) for link in tid]
        urls =[]
        for part ,song in zip(pd,self.songs):
            song = re.sub('[^\w\s]','',song)
            data =  [part[1],part[2],part[3].zfill(2),re.sub(' ','%20',song)]
            urls.append('https://hw-mp3.{}/mixtapes/9/{}/{}%20-%20{}.mp3'.format(*data))
        return urls
        

    def _parse_selection(self,select):
        """Parse all user selection and return the correct songs
           @@params: select  - name or index of song 
        """
        select = 1 if select == 0 else select
        songs = dict(enumerate(self.songs,start=1))
        selection = list(filter(lambda x: select in x \
                            or str(select).lower() in x[1].lower(),
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
                self._song_cache[name]=response
            return data
        return inner


    @_cache
    def play(self, track=None, demo=False):
        """ 
        Play song (uses vlc media player) 
         @@params: track - name or index of song type(str or int)
         @@params: demo  - True: demo sample of song
                              False: play full song 
                              *default: False
        """

        selection = self._parse_selection(track)
        if selection is not None:
            link = self.mp3Urls[selection]
            songname = self.songs[selection]
            
            # Write songname to file
            with open(self._tmpfile.name, "wb") as ws:
                if songname in self._song_cache:
                    print('Grabbing %s from cache'%songname)
                    response  = self._song_cache[songname]
                    content = response.content
                else:
                    print('LINK:',link)
                    response = self._session.get(link)
                    content = response.content
                    status = response.status_code
                    if status != 200:
                        print('\nStatus: %s %s song can not play. Try again '%(status,songname))
                        return 
                song_length = len(content)
                if not demo: # demo whole song
                    chunk = content
                    samp = int(song_length)
                else: # demo partial song
                    samp = int(song_length/5)
                    start = int(samp/5)
                    chunk = content[start:samp+start]
                ws.write(chunk)
                sorf = 'Demo' if demo else 'Full Song'
                print('\n%s %s %s'%('-'*20,sorf ,'-'*20))
                print('Song: %s - %s'%(self.artist,songname))
                print("Size:",converter(samp))
                if not hasattr(self,'player'):
                    self.player = Player()
                self.player.play(self._tmpfile.name)
            return songname,response


    #@_threader
    @_cache
    def download(self,track=False,output="" ,name=None):
        """
        Download song from Datpiff
        @@params: track - name or index of song type(str or int)
        @@output: location to save the song (optional)
        @@name:   rename the song (optional) default will be song's name 
        """

        selection = self._parse_selection(track)
        if selection is None:
            print('\n\t No song found to download')
            return 

        if os.path.isdir(output):
            location = output
        else:
            location = os.getcwd()

        link = self.mp3Urls[selection]
        song = self.songs[selection]
        songname = '/'.join((location, self.artist + " - " + song.strip()+".mp3"))
        print('Saving song as %s'%songname)

        with open(songname, "wb") as ws:
            try:
                response = self._session.get(link)
                response.raise_for_status()
                ws.write(response.content)
                print("\n\t\t-- SONG SAVED --\n", "DIRECTORY: ",location,
                            '\nSONGNAME: ',songname,'\nSIZE:  ',converter(len(response.content)))
                return songname,response
            except:
                    print("Error saving song Non-200 status")


    #@_threader
    def download_album(self,location=None):
        if location:
            if not os.path.isdir(location):
                location= ''
        else:
            location = '' 

        fname = location + "\\"+self.artist + "-" + self.title
        if not os.path.isdir(fname):
            os.mkdir(fname)
        for num, song in enumerate(self.songs):
            with open(fname+"\\"+song+'.mp3', "wb") as aw:
                self.song = num+1
                response = self._session.get(self.mp3Urls)
                if response.status_code == 200:
                    print("Saving: %s.  %s" % (num, song))
                    aw.write(response.content)

        print("\n%s album saved" % self.artist)

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


