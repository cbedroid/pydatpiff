import os
import sys
import re
import atexit
import shutil
from subprocess import PIPE,Popen,check_output
from time import time,sleep
from .baseplayer import BasePlayer 

try:
    import eyed3
except:
    #dummy class
    class eyed3():
        pass

class AndroidError(Exception):
    pass

class Android(BasePlayer):
    TMP = '/sdcard/.pydatpiff_tmp.mp3'
    
    def __init__(self,*args,**kwargs):
        try:
            super(Android,self).__init__(*args,**kwargs)
        except Exception as e:
            print('ANDROID-ERROR:',e)

    @staticmethod
    def _isFile(path):
        """ 
        Check if file path exists 
        :params: path - path of song 
        """
        return os.path.isFile(path)

    def __copyTmp(self):
        """Move media filename from tmp directory into\
        an accessible directory -- see TMP 

        On android platform with root media filename will\
        not be accessible,so we move it to device storage  
        """
        if not self.isFile(self._filename):
            raise PlayerError(msg)

        return shutil.copy(self._filename,self.TMP)


    def _am_start(self,path):
        """ Sets  android java  am-start command  from android sdk"""
        path = path[1:] if path.startswith('/') else path
        start = "am start --user 0 -a android.intent.action.VIEW "
        return  start +"-d file:///%s -t audio/*"%path

                
    def __len__(self):
        try:
            return len(self.__content)
        except:
            return 0


    def _is_playing(self,boolean=False):
        """ Return whether a song is being played or paused.
            
            variable state - belongs to BasePlayer
        """
        self._state.update(dict(playing=bool(boolean),pause=not bool(boolean)))

    @property
    def duration(self):
        return self.__eyed3.info.time_secs 


    def _format_time(self,pos=None):
        """Format current song time to clock format """
        pos = self.duration  if not pos else pos
        mins = int(pos/60)
        secs = int(pos%60)
        return  mins,secs


    @property
    def artist(self):
        """ Artist name"""
        if hasattr(self,"_artist"):
            return self._artist
        
    @artist.setter
    def artist(self,name):
        self._artist = name


    @property
    def album(self):
        """ Album name"""
        if self.__tag:
            return self.__eyed3.tag.album

    @property
    def title(self):
        """ Song name"""
        return self._title


    @title.setter
    def title(self,name):
        self._title = name


    def _splitSong(song,keep=1):
        """Parse song and split by '-' """
        #TODO: remove or refactor this for baseclass
        if "-" in song:
            return song.split("-")[keep]
        return song
        

    def _setTrackInfo(self):
        """Set the artist name  and title of the song"""
        #::TODO refactor this for baseclass
        try:
            song = self._filenames[self._index]
            title = re.sub(".mp3","",os.path.basename(song))
            self.artist = self._splitSong(title,0)
            self.title = self._splitSong(title,-1)
        except:
            tag = self.__eyed3.tag.title 
            self.artist = self.__eyed3.tag.artist
            self.title = self._splitSong(self.__eyed3.tag.title,1)
        
    

    @property
    def __bytes_elaspe(self):
        """Current bytes of the current song"""
        return self.bytes_per_sec * self.current_time


    @property
    def current_time(self):
        """Current position of track in seconds"""
        if hasattr(self,'_load_time'):
            return int(time() - self._load_time) 
        return 1

    @current_time.setter
    def current_time(self,spot):
        self._load_time = time() + spot


    @property
    def bytes_per_sec(self):
        """song bytes per seconds"""
        return len(self) / self.__eyed3.info.time_secs


    def __setContent(self,position):
        """Write media content to file"""
        br = self.bytes_per_sec
        length = int(br* int(self.current_time + position))
        self.current_time = position 
        print('\nSetting %s of %s'%(self.current_time,self.duration))
        if length < 0:
            # need to get the ffwd out of range too 
            print('out of track range',)
            return 
        print('\nsetting Content:',length)
        with open(self.TMP,'wb') as _tmp:
            _tmp.write(self.__content[length:])
        return length

    @property
    def songpath(self):
        if hasattr(self,'_songpath'):
            return self._media_song_path:
        else:
            # clean this up with custom Error
            raise TypeError('Android song path not  found')


    @songpath.setter
    def songpath(self,path):
        self._media_song_path = path


    def preloadTrack(self,path=None):
        """
        Open file path  and return its content
        @params:: path - path of the song
        """
        if not self._state.get('load'):
            self._load_time = time()

        self._state['pause'] = False
        self.__eyed3 = eyed3.load(self.songpath)
        self.__tag = self.__eyed3.tag
        f = open(self.songpath,'rb')
        self.__content = f.read()
        f.close()
        self._state['load'] = True
        print('loadingMedia:',self._state)

    def setTrack(self,name,filename):
        print('Setting Track',name,filename)

        self.songpath = filename
        self._song = name
        if name and filename:
            self._name = name
            self._filename = filename
            self.is_track_set = True
        else:
            print('No media to play')

    @property
    def play(self):
        self._state = dict(playing=False,pause=False,
                              load=False,stop=False)
        self._play()


    def _play(self,song=None ,position=1):
        """
        Play media songs
        :params: song - song  play 
            type:: int - index of songs  (see Android.songs)
                   str - path of the song to play 
            pos   - play a song at the given postion (seconds)
        """ 
        if not self._state.get('load'):
            self._load_time = time()
            self._state['load'] = True;
        self.preloadTrack()

        if self._state['pause']: # detect if player is paused
            # Set the pause position to the current position
            position = self._paused_pos
        
        self.__setContent(position)
        self._player = Popen(self._am_start(self.TMP),shell=True,stdin=PIPE,
                    stdout=PIPE,stderr=PIPE)

        self._is_playing(True)
  

    def volume(self,vol=None):
        """
        Android volume controls
        @params:: vol - set the media volume range 0 - 100 
        """
        os.system('termux-volume music %s'% vol)

   
    @property
    def pause(self):
        """Pause song"""
        # capture the position the media player was pause
        if not self._state['pause']:
            self.stop
            print("Pause")
            self._paused_pos = self.current_time
            self._is_playing(False)

        else: # unpause
            self.current_time = self._paused_pos
            print("Unpause")
            self._play()
            # Not here play() will handle self._is_playing(True) 


    def _seeker(self,pos=5, rew=True):
        """Control fast forward and rewind function"""
        spot = pos
        if self._state['pause']:
            self.current_time = self._paused_pos
            self._state['pause'] = False

        #self.current_time = spot
        self._play(postion=pos)


    def rewind(self,pos=5):
        self._seeker(-pos,True)
        

    def ffwd(self,pos=5):
        self._seeker(pos,False)

    @property
    def stop(self):
        service = "am stopservice "
        cmd = service + "org.videolan.vlc/org.videolan.vlc.PlaybackService"
        results = Popen(cmd,shell=True,stdout=PIPE,stderr=PIPE)

