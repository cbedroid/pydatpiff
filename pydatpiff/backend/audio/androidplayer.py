import os
import sys
import re
import atexit
import shutil
from subprocess import PIPE,Popen,check_output
from time import time,sleep
<<<<<<< HEAD
=======
from glob import glob
from functools import wraps
>>>>>>> e75e8dfe19155bdbd5f678c31715c178e6cdf6d5
from .baseplayer import BasePlayer 

try:
    import eyed3
except:
    #dummy class
    class eyed3():
        pass

class AndroidError(Exception):
    pass

TMP = '/sdcard/.pydatpiff_tmp'
class Android(BasePlayer):
<<<<<<< HEAD

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.state['pause'] = False

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

=======
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.song = self.TMP_FILE
        self.state['pause'] = False
>>>>>>> e75e8dfe19155bdbd5f678c31715c178e6cdf6d5

    def _am_start(path):
        """ Sets  android java  am-start command  from android sdk"""
        path = path[1:] if path.startswith('/') else path
        start = "am start --user 0 -a android.intent.action.VIEW "
        return  start +"-d file:///%s -t audio/mp3"%path

                
    def __len__(self):
        return len(self.__content)


    def _is_playing(boolean=False):
        """ Return whether a song is being played or paused.
            
            variable state - belongs to BasePlayer
        """
        self.state = dict(playing=bool(boolean),pause=not bool(boolean))

    @property
    def track_size(self):
        return self.__eyed3.info.time_secs 


    def _format_time(self,pos=None):
        """Fomrat current song time to clock format """
        pos = self.track_size  if not pos else pos
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


    @staticmethod
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
        return self.__bytes_per_sec * self.__position


    @property
    def __position(self):
        """Current position of track in seconds"""
        if hasattr(self,'_start_time'):
            return int(time() - self._start_time)
        return 1

    @__position.setter
    def __position(self,spot):
        self._start_time = time()-spot


    @property
    def __bytes_per_sec(self):
        """song bytes per seconds"""
        return len(self) / self.__eyed3.info.time_secs


    def __setContent(self,length):
        """Write media content to file"""
        br = self.__bytes_per_sec
        length = int(br* int(self.__position + length))
        with open(self.TMP,'wb') as _tmp:
            _tmp.write(self.__content[length:])
        return length


    def loadMedia(self):
        """
        Open file path  and return its content
        @params:: file - path of the song
        """
        self._state['pause'] = False
        self.__eyed3 = eyed3.load(file)
        self.__tag = self.__eyed3.tag
        f = open(self.filename,'rb')
        self.__content = f.read()
        f.close()


    def setTrack(name,filename):
        if name and filename:
            self._name = name
            self._filename = filename
            self.is_track_set = True
        else:
            print('No media to play')

    def play(self,song=None ,pos=1):
        """
        Play media songs
        @params:: song - song  play 
                    type:: int - index of songs  (see Android.songs)
                           str - path of the song to play 
                  pos   - play a song at the given postion (seconds)
        """
        self._start_time = time()
        self.loadMedia()

        if self.state['pause']: # detect if player is paused
            # Set the pause position to the current position
            pos = self._paused_pos
        
        self.__setContent(pos)
        self._player = Popen(self._command,shell=True,stdin=PIPE,
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
        if not self.state['pause']:
            self.stop
            print("Pause")
            self._paused_pos = self.__position
            self._is_playing(False)

        else: # unpause
            self.__position = self._paused_pos
            print("Unpause")
            self.play()
            # Not here play() will handle self._is_playing(True) 


    def _seeker(self,pos=5, rew=True):
        """Control fast forward and rewind function"""
        spot = pos
        if self.state['pause']:
            self.__position = self._paused_pos
            self.state['pause'] = False

        self._start_time+=spot
        self.play(pos=pos)


    def rewind(self,pos=5):
        self._seeker(pos,True)
        

    def ffwd(self,pos=5):
        self._seeker(-pos,False)

    @property
    def stop(self):
        service = "am stopservice "
        cmd = service + "org.videolan.vlc/org.videolan.vlc.PlaybackService"
        results = Popen(cmd,shell=True,stdout=PIPE,stderr=PIPE)

