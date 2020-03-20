import re
from time import time 
from functools import wraps
from .audio_engine import Popen,MetaData
from .baseplayer import BasePlayer
from ..filehandler import Path
from ..config import Threader
from ...errors import MvpError
from ...frontend.display import Print



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


    def _format_time(self,pos=None):
        """Format current song time to clock format """
        pos = self.duration  if not pos else pos
        mins = int(pos/60)
        secs = int(pos%60)
        return  mins,secs


    @Threader
    def registerPauseEvent(self):
        """
        Captures the time duration when the track is paused.
        Once track is unpause time will be added to the original track time
        (MPV._time_elapse).
        This time will be used to calculate the accuracy of current_position
        when pause state changes from pause to playing.
        """

        start = time()
        rollback = 0
        while self.state['pause']:
            if time() - start >=1:
                rollback+=1
                start = time()

            if not self.state['pause']:
                self._time_elapse +=  rollback
                break


    @property
    def _last_paused_time(self):
        """Returns the last time track was paused"""
        return self.__previous_time
        

    @_last_paused_time.setter
    def _last_paused_time(self,timer):
        self.__previous_time = timer


    @property
    def current_position(self):
        """Current position's time of track"""

        timer = 0
        if hasattr(self,'_time_elapse'):
            timer = time() - self._time_elapse
            if self.state['pause']: # track was paused
                return self._last_paused_time

        self._last_paused_time = timer
        if self.state['stop']: # track stop 
            return 0
        return timer


    @current_position.setter
    def current_position(self,position):
        self._time_elapse += position


    @property
    def duration(self):
        """Return track length  in seconds"""
        return self._metadata.trackDuration


    def _resetState(self,**kwargs):
        """Reset all track's states (see Android.state)"""
        self._state = dict(playing=False,pause=False,
            load=False,stop=False)
        self._state.update(**kwargs)


    def _write_cmd(self,cmd):
        """
        Write command to Popen stdin
        param: cmd - string character to write
        """

        if  hasattr(self,'_popen'):
            if self.state['load'] and self._popen.is_running: 
                self._popen.stdin.write('{}\n'.format(cmd).encode('utf8'))
                self._popen.stdin.flush()
                return 


    def setTrack(self,name,path):
        self._virtual_time = 0

        if Path.isFile(path):
            self._song = name
            self._song_path = path
            self._metadata = MetaData(path)
        else:
            raise MvpError(1)

        Popen.unregister()
        self._popen = Popen(self._pre_popen(self._song_path))
     

    @property
    def play(self):
        #setTrack will handle track loading 
        if self.state['pause'] and self._popen.is_running:
            self.pause
            return 

        elif not self.track_is_loaded:
            self._popen.register(callback=self._resetState)
            self._time_elapse = time()
            self._is_playing(True) 
            self.state['load'] = True


    @property
    def pause(self):
        """Pause and unpause the track."""
        if self.state['load']:

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
            if self.state['pause']:
                self.registerPauseEvent()

        else:
            print('No track is playing')
            return -1


    def _adjustTrackTime(self,sec):
        """
        Adjust the track's time in seconds when track is
        alter either by rewind,fast-forward, or paused.
        """
        constrains = self.constrain_seek(sec)
        self._time_elapse += constrains 
        self.__previous_time += -constrains 


    def constrain_seek(self,seek):
        """
        Force constraints on setting virtual timer,
        when rewinding and fast-fowarding.
        """
        seek = float(seek)
        current_pos = self.current_position
        if current_pos  + seek < 0:
            return 0

        return int(seek) * -1


    def _duration_callback(f):
        """
        Callback function that force track time to be alter
        whenever track position is being seeked see: MPV._seeker.
        """
        @wraps(f)
        def inner(self,time_sec):
            self._adjustTrackTime(time_sec)
            return  f(self,time_sec)
        return inner
    


    @_duration_callback
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
        self.state['stop'] = True
        Popen.unregister()

