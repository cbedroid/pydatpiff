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
                    '--input-file=/proc/self/fd/0',
                    '--no-term-osd',
                    '--osc=yes',
                    '--force-window',
                    '%s'%song 
                    ]

    def setTrack(self,name,path):
        self._virtual_time = 0

        if Path.isFile(path):
            self._song = name
            self._song_path = path
            self._metadata = MetaData(path)
        else:
            raise MvpError(1)
        
        
    def _format_time(self,pos=None):
        """Format current song time to clock format """
        pos = self.duration  if not pos else pos
        mins = int(pos/60)
        secs = int(pos%60)
        return  mins,secs

        
    @property
    def current_position(self):
        if hasattr(self,'virtual_timer'):
            return time() - self.virtual_timer
        return 0

    @current_position.setter
    def current_position(self,position):
        self.virtual_timer += position


    @property
    def duration(self):
        return self._metadata.trackDuration


    def _write_cmd(self,cmd):
        """
        Write command to Popen stdini
        param: cmd - string character to write
        """
        self._popen.stdin.write('{}\n'.format(cmd).encode('utf8'))
        self._popen.stdin.flush()
    

    @property
    def play(self):
        #setTrack will handle track loading 
        self._popen = Popen(self._pre_popen(self._song_path))
        self.virtual_timer = time()



    @property
    def pause(self):
        cmd = { True:'no',
                False:'yes'
              } 

        # set pause according to the state of pause.
        # pause then unpause and vice versa
        pause = 'set pause {} \n'.format(cmd[self.state['pause']])
        self._write_cmd(pause)
        self.state['pause'] = bool(cmd)
      
    def time_callback(f):
        """
        Adjust track time to the current position of the track.
        """
        @wraps(f)
        def inner(self,time_sec):
            adjustment = f(self,time_sec)
            self.virtual_timer -=adjustment
            return 
        return 
    
    def _seeker(self,sec=5):
        raw_sec = re.sub(r'\-','',str(sec))
        if not raw_sec.isnumeric():
            Print('Must use numerical numbers')
            return 
        seek = 'seek %s \n'%sec
        self._write_cmd(seek)


    #@time_callback
    def rewind(self,sec=5):
        sec = '-' + str(sec)
        self._seeker(sec)
        
        # no need to catch TypeError while converting to int
        # if seeker pass then obviously the data type is numeric.
        
        return int(sec)

    #@time_callback
    def ffwd(self,sec):
        sec = str(sec)
        self._seeker(sec)
        return int(sec)
            

    @property
    def stop(self):
        self._write_cmd('quit \n')
    


