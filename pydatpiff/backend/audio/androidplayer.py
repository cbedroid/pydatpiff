import os
import re
import sys 
from subprocess import PIPE,Popen
from time import time
from ..filehandler import Path
from .baseplayer import BasePlayer

try:
    # try to import eyed3 for easy metadata
    import eyed3
except:
    class eyed3():
        pass

class AndroidError(Exception):
    pass


class Android(BasePlayer):
    # Because of android's permission not allowing non-root users to 
    # to access write permissions on low-level filesystem,
    # we will move the tempfile (see backend.filehandler)
    # to the device storage system ('/sdcard' or '/storage/')
    DROID_TMP = '/sdcard/.pydatpiff_tmp.mp3'
    __Id3 = eyed3

    def __init__(self,*args,**kwargs):
        """ Initialize BasePlayer from Android class"""
        super(Android,self).__init__(*args,**kwargs)
    
    def __len__(self):
        return len(self.__content)

    def __resetState(self):
        self._state = dict(playing=False,pause=False,
            load=False,stop=False)

    @property
    def __am_start_Intent(self):
        """ Prepares android java 'am start' intent to play song""" 
        path = re.sub('\B\/','',self.DROID_TMP) #remove start '/'
        intent = 'am start --user 0 -a android.intent.action.VIEW -d '
        return intent + 'file:///{} -t audio/*'.format(path)
    
        
    @property
    def duration(self):
        return self.__Id3.info.time_secs 
   
        
    @property
    def songpath(self):
        """ Returns media song path from media class"""
        if hasattr(self,'_media_song_path'):
            return self._media_song_path
        else:
             raise AndroidError('Media song path not found')
    
    @songpath.setter
    def songpath(self,path):
        if Path.isFile(path):
            # keep a copy of the original path to extract the meta data
            self.__meta_data_path = path
            self._media_song_path = path
        else: 
            error = 'internal Error: android media path %s not found'%path
            raise AndroidError(error)


    def setTrack(self,name,path):
        """ 
        Prepares the media tracks and set its attributes and current state

        :params: name - name of the of the media track
        :param: path - path location of the media track
        """
        
        self.__resetState()
        if Path.isFile(path):
            self._name = name
            self.songpath = path
            print('Setting Track',name,path)
        else:
            print('No media to play')


    def _format_time(self,*arg,**kwargs):
        return 0


    def preloadTrack(self):
        """Open file path  and return its content"""

        if not self._state.get('load'):
            self._load_time = time()
        self._state['pause'] = False
        self.__Id3 = eyed3.load(self.__meta_data_path)
        self.__tag = self.__Id3.tag
        with open(self.songpath,'rb') as f:
            self.__content = f.read()

        self._state['load'] = True
        print('loadingMedia:',self._state)

    @property
    def bytes_per_sec(self):
        """song bytes per seconds"""
        return len(self) / self.__Id3.info.time_secs

    @property
    def current_time(self):
        """Current position of track in seconds"""
        if hasattr(self,'_load_time'):
            return int(time() - self._load_time) 
        return 1

    @current_time.setter
    def current_time(self,spot):
        self._load_time = time() + spot




    def __setContent(self,position):
        """
        Write media content to file
        
        :param: position  - postion to start song (second(s)) 
        """

        br = self.bytes_per_sec
        length = int(br* int(self.current_time + position))
        self.current_time = position 
        print('\nSetting %s of %s'%(self.current_time,self.duration))
        if length < 0:
            # need to get the ffwd out of range too 
            print('out of track range',)
            return 
        print('\nsetting Content:',length)
        with open(self.DROID_TMP,'wb') as _tmp:
            _tmp.write(self.__content[length:])
        return length


    @property
    def play(self):
        self._play()

    def _play(self,position=0):
        """
        Play media songs
        :param:pos   - play a song at the given postion (seconds)
        """ 
        self.preloadTrack()

        if self._state['pause']: # detect if player is paused
            # Set the pause position to the current position
            position = self._paused_pos
        
        self.__setContent(position)
        self._player = Popen(self.__am_start_Intent ,shell=True,
                    stdin=PIPE,stdout=PIPE,stderr=PIPE)

        #self._is_playing(True)
  
