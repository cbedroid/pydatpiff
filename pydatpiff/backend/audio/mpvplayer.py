import os 
import re
import fcntl
import subprocess as sp
from time import time 
from functools import wraps
from ..filehandler import Path
from ...frontend.display import Print
from ...errors import MvpError
from .audio_engine import Popen,MetaData
from .baseplayer import BasePlayer


class MPV(BasePlayer):

    def __init__(self):
         self._popen = None
         self._state={'playing':False,'pause':False,
                 'stop':False,'load':False}

    
    def _pre_popen(self,song):
        return ['mpv',
                '--input-terminal=yes',
                '-no-audio-display',
                '--input-file=/proc/self/fd/0',
                '--no-term-osd',
                '--osc=no',
                '%s'%song 
                ]

        #'--force-window',

       

    def _format_time(self,pos=None):
        """Format current song time to clock format """
        pos = self.duration  if not pos else pos
        mins = int(pos/60)
        secs = int(pos%60)
        return  mins,secs

        
    @property
    def current_position(self):
        timer = 0
        if hasattr(self,'_time_elapse'):
            timer = time() - self._time_elapse

            if self.state['pause']:
                return self.__last_time_update

        self.__last_time_update = timer
        return timer

    @current_position.setter
    def current_position(self,position):
        self._time_elapse += position



    @property
    def duration(self):
        """Return track length  in seconds"""
        return self._metadata.trackDuration


    def _resetState(self,**kwargs):
        """Reset all state of track (see Android.state)"""
        self._state = dict(playing=False,pause=False,
            load=False,stop=False)
        self._state.update(**kwargs)


    def _write_cmd(self,cmd):
        """
        Write command to Popen stdin
        param: cmd - string character to write
        """

        if  hasattr(self,'_popen'):
            if self.state['load'] and self._popen is None: 
                self._popen.stdin.write('{}\n'.format(cmd).encode('utf8'))
                self._popen.stdin.flush()
                return 
        Print('No Track loaded')


    def setTrack(self,name,path):
        self._virtual_time = 0

        if Path.isFile(path):
            self._song = name
            self._song_path = path
            self._metadata = MetaData(path)
        else:
            raise MvpError(1)
        self.state['load'] = True
     

    @property
    def play(self):
        #setTrack will handle track loading 
        if self._is_playing() and self._popen.poll() is None:
            self.pause
            return 
        
        self._popen = Popen(self._pre_popen(self._song_path))
        self._popen.register(callback=self._resetState)
        self._time_elapse = time()
        self._is_playing(True) 


    @property
    def pause(self):
        """Pause and unpause the track."""

        cmd = { True:'no',
                False:'yes'
              } 
        # set pause according to the state of pause.
        # if state is paused then unpause and vice versa.
        state = cmd[self.state['pause']]
        pause = 'set pause {} \n'.format(state)
        self._write_cmd(pause)

        last_pause_state = self.state['pause']
        current_pos = self.current_position

        self._is_playing(last_pause_state)
        # if the track is pause then capture the time it was pause 
        if self.state['pause']:
            self.__last_time_update = self.current_position


    def _adjustTrackTime(self,sec):
        """
        Adjust the track's time in seconds when track is
        alter either by rewind,fast-forward, or paused.
        """
        self._time_elapse += self.contrain_seek(sec)


    @property
    def contrain_seek(self,seek):
        """
        Force constraints on setting virtual timer,
        when rewinding and fast-fowarding.
        """
        current_pos = self.current_position
        if current_pos  - seek < 0:
            return 0
        else:
            return int(self.duration) * -1

    def time_callback(f):
        """
        Callback function that force track time to be alter
        whenever track position is being seeked.
        """
        @wraps(f)
        def inner(self,time_sec):
            self._adjustTrackTime()
            return  f(self,time_sec)
        return inner
    


    @time_callback
    def _seeker(self,sec=5):
        """
        Control fast forward and rewind function.

        :param: pos - time to rewind or fast-forward (in seconds)
        """

        raw_sec = re.sub(r'\-','',str(sec))
        if not raw_sec.isnumeric():
            Print('Must use numerical numbers')
            return 
        seek = 'seek %s \n'%sec
        self._write_cmd(seek)
        return int(sec)


    def rewind(self,sec=5):
        """
        Rewind track.

        :param: pos - time to rewind or fast-forward (in seconds)
        """

        sec = '-' + str(sec)
        self._seeker(sec)
        
        # no need to catch TypeError while converting to int
        # if seeker pass then obviously the data type is numeric.
        

    def ffwd(self,sec):
        """
        Fast-forward track.

        :param: pos - time to rewind or fast-forward (in seconds)
        """

        sec = str(sec)
        self._seeker(sec)
            

    @property
    def stop(self):
        """Stop the current track from playing."""
        self._write_cmd('quit \n')
        self._resetState()
        self._popen.kill()

