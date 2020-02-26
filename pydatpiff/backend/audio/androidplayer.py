import os
import re
import sys 
from time import time
from subprocess import PIPE,Popen
from mutagen.mp3 import MP3
from ..filehandler import Path
from ..config import Threader
from .baseplayer import BasePlayer

class AndroidError(Exception):
    pass


class Android(BasePlayer):
    # Because of android's permission not allowing non-root users to 
    # to access write permissions on low-level filesystem,
    # we will move the tempfile (see backend.filehandler)
    # to the device storage system ('/sdcard' or '/storage/')
    DROID_TMP = '/sdcard/.pydatpiff_tmp.mp3'
    __Mutagen = MP3

    def __init__(self,*args,**kwargs):
        """ Initialize BasePlayer from Android class"""
        super(Android,self).__init__(*args,**kwargs)
    
    def __len__(self):
        return len(self.__content)

    def _resetState(self,**kwargs):
        self._state = dict(playing=False,pause=False,
            load=False,stop=False)
        self._state.update(**kwargs)

    def _is_playing(self,boolean=False):
        """ Return whether a song is being played or paused.
            
            variable state - belongs to BasePlayer
            sets the playing state = boolean
            sets the pause state = not boolean
        """
        self.state.update(dict(playing=bool(boolean),pause=not bool(boolean)))



    @property
    def elapse(self):
        """ 
        Elapse is the last time since a track has been loaded (self.__load).
        Elaspe capture when player is playing track
        It records the time from the latest state in seconds
        """
        return self._elapse

    @elapse.setter
    def elapse(self,val=0):
        #state_time was here
        self._elapse = (time() - self._load_time )


    @Threader
    def _real_time_elapse(self):
        """
        Starts and stop the elapse time according to the player state.
        Elapse time (real clock time) will start when player state is 'playing'
        and stop when player state is 'paused'.
        This time will be used to calculate the accuracy of current_position
        when loading the content of a track when player state changes from
        pause to playing and vice versa.
        """
        print('\nClock started')
        start = time()
        while True:
            if self._state['playing'] and not self._state['pause']:
                #state_time was here
                self._elapse = time() - self._load_time
            #else: #catch the current postion  paused,rewinf, and fast-forward 
            #    # its self.elapse because self.elapse has the pause position
            #    self.current_position = 0
            if time() - start > 3:
                start = time()

            if hasattr(self,'__content'):
                if self.current_position > (len(self)/self.bytes_per_sec)\
                        and self._state['playing']:
                    print('\nTrack finish')
                    self._resetState()

    @property
    def __am_start_Intent(self):
        """ Prepares android java 'am start' intent to play song""" 
        path = re.sub('\B\/','',self.DROID_TMP) #remove start '/'
        intent = 'am start --user 0 -a android.intent.action.VIEW -d '
        return intent + 'file:///{} -t audio/*'.format(path)
    
        
    @property
    def duration(self):
        return self.__Mutagen.info.length
   
        
    @property
    def _song_path(self):
        """ Returns media song path from media class"""
        if hasattr(self,'_media_song_path'):
            return self._media_song_path
        else:
             raise AndroidError('Media song path not found')
    
    @_song_path.setter
    def _song_path(self,path):
        if Path.isFile(path):
            # keep a copy of the original path to extract the meta data
            self.__meta_data_path = path
            self._media_song_path = path
        else: 
            error = 'internal Error: android media path %s not found'%path
            raise AndroidError(error)


    
    def _format_time(self,pos=None):
        """Format current song time to clock format """
        pos = self.duration  if not pos else pos
        mins = int(pos/60)
        secs = int(pos%60)
        return  mins,secs


    def __preloadTrack(self):
        """Open file path  and return its content"""

        self.__Mutagen = MP3(self.__meta_data_path)

        with open(self._song_path,'rb') as f:
            self.__content = f.read()
        self._state['load'] = True


    @property
    def bytes_per_sec(self):
        """song bytes per seconds"""
        return len(self)/self.duration

    @property
    def _pause_position(self):
        """ Return the position when the pause is pause"""
        if not hasattr(self,'_pause_pos'):
            setattr(self,'_pause_pos',self.current_position)
            return 0
        return self._pause_pos

    @_pause_position.setter
    def _pause_position(self,pos):
        self._pause_pos = pos


    @property
    def current_position(self):
        pos = time() - self._start_time
        """
        if self.state['pause']:
            if hasattr(self,'_pause_pos'):
                return self._pause_pos
            else:
                setattr(self,'_pause_pos',pos)
        """
        return pos if pos > 0 else 0 

    @current_position.setter
    def current_position(self,pos):
        self._start_time -= pos

    def __load(self,position):
        """
        Write media content to file
        
        :param: position  - postion to start song (second(s)) 
        """
        #spot in seconds
        with open(self.DROID_TMP,'wb') as mp3:
            if self.state['pause']:
                difference = self.current_position - (
                                self._pause_position + position
                                )
                print('PAUSE_POSITION:',self._pause_position)
                print('OLD CurrentPosition:',self.current_position)
                print('Difference:',difference)
                self.current_position = -(difference)
                print('New CurrentPosition:',self.current_position)
            else:
                self.current_position = position

            spot = int(self.current_position+position) 
            topos = spot*self.bytes_per_sec if spot > 0 else 1*self.bytes_per_sec
            topos = int(topos)

            self._load_time = time()
            mp3.write(self.__content[topos:])


    def setTrack(self,name,path):
        """ 
        Prepares the media tracks and set its attributes and current state

        :params: name - name of the of the media track
        :param: path - path location of the media track
        """
        self._resetState()

        if Path.isFile(path):
            self._song = name
            self._song_path = path
        else:
            raise AndroidError('Internal Error: Media song invalid path')

        self._load_time = time()
        self.elapse = 0

    @property
    def play(self):
        self._real_time_elapse()
        self._start_time = time()
        self._play()


    def _play(self,position=0):
        """
        Play media songs
        :param:pos   - play a song at the given postion (seconds)
        """ 
        self.__preloadTrack()

        if not self._state['load']:
            self.__startClock()
            self._state['load'] = True

        self.__load(position)
        self._player = Popen(self.__am_start_Intent ,shell=True,
                    stdin=PIPE,stdout=PIPE,stderr=PIPE)
        self._state['pause'] = False
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
            # USE VERBOSE FOR PRINT
            print("Paused")
            self._is_playing(False)
            #Capture time when state is pause 
            self._pause_position = self.current_position

        else: # unpause
            print("Unpause")
            self._play()

    def _seeker(self,pos=5, rew=True):
        """Control fast forward and rewind function"""
        spot = pos
        if self._state['pause']:
            self._state['pause'] = False

        #self.current_position = spot
        self._play(position=pos)


    def rewind(self,pos=5):
        self._seeker(-(pos),True)
        

    def ffwd(self,pos=5):
        self._seeker(pos,False)

    @property
    def stop(self):
        service = "am stopservice "
        cmd = service + "org.videolan.vlc/org.videolan.vlc.PlaybackService"
        results = Popen(cmd,shell=True,stdout=PIPE,stderr=PIPE)
        
