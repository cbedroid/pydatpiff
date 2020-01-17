from ...frontend.display import Print
from ...errors import PlayerError


class BasePlayer:
    """Media player controller""" 
    def __init__(self,*args,**kwargs):
        self._state={'playing':False,'pause':False,
                 'stop':False,'load':False}
        self._is_track_set = False
        self.player = None 
    
    @property
    def filename(self):
        if not hasattr(self,'_filename'):
            raise PlayerError(2,'Cannot find song')
        return self._filename

    @property
    def name(self):
        if not hasattr(self,'_song'):
            raise PlayerError(2,'Cannot find name of song')
        return self._song

    
    def set_all_state(self,state=False,**kwargs):
        """Change all states at once"""
        if self.state:
            for k,v in self.state.items():
                self.state[k] = state
        self.state.update(**kwargs)

    @property
    def state(self):
        """Current state of the song being played"""
        if hasattr(self,'_state'):
            return self._state
        else:
            raise PlayerError(3,'def _state')

    @state.setter
    def state(self,**state):
        self._state.update(**state)


    def setTrack(self,*args,**kwargs):
        raise NotImplementedError


    def _format_time(self,*args,**kwargs):
        """Format current song time to clock format"""
        raise NotImplementedError


    @property
    def info(self):
        """Returns feedback for media song being played"""
        if not self.state['load']:
            return 'No media' 
        c_min,c_sec = self._format_time(self.track_time)
        c_sec = c_sec if len(str(c_sec)) >1 else str(c_sec).zfill(2) 

        l_min,l_sec = self._format_time(self.track_size)
        l_sec = l_sec if len(str(l_sec)) >1 else str(l_sec).zfill(2) 
        
        if self.state['playing']:
            mode = 'Playing' 
        elif self.state['pause']:
            mode = 'Paused'
        else:
            mode = 'Stopped'
        Print('TRACK:',self.name)
        Print('MODE:',mode)
        pos = 'POSITION: {0}:{1} - {2}:{3}'.format(c_min,c_sec,l_min,l_sec)
        Print(pos)

    @property
    def _volumeLevel(self):
        """ Current media player volume"""
        #TODO implement method to monitor the volume
        return -1
    
    def _set_volume(self,*args,**kwargs):
        raise NotImplementedError

    
    def volumeUp(self,vol=5):
        """Turn the media volume up"""
        raise NotImplementedError
     

    def volumeDown(self,vol=5):
        """Turn the media volume down"""
        raise NotImplementedError
 

    def volume(self,vol=None):
        """Set the volume to exact number"""
        raise NotImplementedError

   
    @property
    def play(self):
        """ Play media song"""
        raise NotImplementedError

    @play.setter
    def play(*args,**kwargs):
        raise NotImplementedError
        

    @property
    def pause(self):
        """Pause the media song"""
        raise NotImplementedError

    def _seeker(self,pos=10,rew=True):
        """ Rewind and ffwd base controls"""
        raise NotImplementedError


    def rewind(self,pos=10):
        """
        Rewind the media song
             vlc time is in milliseconds
             @params: pos:: time(second) to rewind media. default:10(sec)
        """
        raise NotImplementedError


    def ffwd(self,pos=10):
        """Fast forward media 
             vlc time is in milliseconds
             @params: pos:: time(second) to rewind media. default:10(sec)
        """
        raise NotImplementedError

       
    @property
    def stop(self):
        """ Stops the song """
        raise NotImplementedError

