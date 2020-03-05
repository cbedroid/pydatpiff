import threading
from time import sleep,time
from ...frontend.display import Print
from ...errors import PlayerError
from ..config import Threader

class DerivedError(Exception):
    pass


'''
#TODO:name_change
    duration (inherited)  ->> duration
'''
class BaseMeta(type):
    """
    For Authors and Contributors only !
    Metaclass that will force constrains on any derived class that inherit BasePlayer

    Certain functions must be available in derived subclass.
    All of the functions and method will be force here
    """
    def __new__(cls,name,bases,body):
        methods =['setTrack', '_format_time','duration']
        # current_position,_song

        for method in methods:
            if method not in body:
                error = 'Method: "%s.%s" must be implemented in derived class '\
                        '"%s" to use BasePlayer'%(name,method,name)
                raise DerivedError(error)
        return super().__new__(cls,name,bases,body)


class BasePlayer(metaclass=BaseMeta):
    """Media player controller""" 
    def __init__(self,*args,**kwargs):
        self._state={'playing':False,'pause':False,
                 'stop':False,'load':False}
        self.__is_monitoring = False
        self._monitor()

    @property
    def name(self):
        if not hasattr(self,'_song'):
            raise PlayerError(2,'Cannot find a name for the song playing')
        return self._song

    
    def _set_all_state(self,state=False,**kwargs):
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

    def _is_playing(self,boolean=False):
        """ 
        Set the state of playing and pause.

        param: boolean - True or False
                True: sets playing True and pause False 
                False: sets playing False and pause True 
        """
        self.state.update(dict(playing=bool(boolean),pause=not bool(boolean)))

    @staticmethod
    def __wait(delay):
        start = time()
        while (time() - start) < 10:
            pass

    def _didTrackStop(self,mode=1): 
        """Check if track has ended"""
        WAIT = 2
        current = self._format_time(self.current_position)
        end = self._format_time(self.duration)

        if current >= end:
            #recheck position to see if track has ended or its a false positive
            if mode == 1:
                re_check = time()
                while (time() - re_check) < WAIT:
                    pass
                return _didTrackStop(mode=2)

            print('Monitoring changed state\n',self.state)
            self._set_all_state(False,stop=True)
            return True


    @Threader
    def _monitor(self):
        """
        Monitor media track and automatically set state
        when media state changes.
        """
        while not self.__is_monitoring:
            if self.state['playing']:
                self._is_playing(True)
                self.__is_monitoring = True
        print('Monitoring')
        # If media.autoplay changes track before song finish 
        # adjust sleep time 

        # wait for 3 sec, if the track is load then monitor when the track stops
        SLEEP_TIME = 3
    
        if True:
            self.__wait(10)
            print('\n\n%s\nmonitoring\n%s'%(30*'-',30*'-'))

            while self.state['load']:
                playing = self.state.get('playing')
                if playing:
                    #sleep(SLEEP_TIME) 
                    self.__wait(SLEEP_TIME) # wait for track to load
                    current_position = self._format_time(self.current_position)
                    endtime = self._format_time(self.duration)
                    print('Current: %s End: %s'%(current_position,endtime))

                    if self._didTrackStop():
                        break

            #If track is stop then recall function for next track
            self.__is_monitoring = False
            self._monitor() # recursive callback           
        
    def setTrack(self,*args,**kwargs):
        raise NotImplementedError

    @property
    def duration(self,*args,**kwargs):
        raise NotImplementedError

    def _format_time(self,*args,**kwargs):
        """Format current song time to clock format"""
        raise NotImplementedError


    @property
    def info(self):
        """Returns feedback for media song being played"""
        if not self.state['load']:
            return 'No media' 
        c_min,c_sec = self._format_time(self.current_position)
        c_sec = c_sec if len(str(c_sec)) >1 else str(c_sec).zfill(2) 

        l_min,l_sec = self._format_time(self.duration)
        l_sec = l_sec if len(str(l_sec)) >1 else str(l_sec).zfill(2) 
        
        if self.state['playing']:
            mode = 'Playing' 
        elif self.state['pause']:
            mode = 'Paused'
        else:
            mode = 'Stopped'
        print('TRACK:',self.name)
        print('MODE:',mode)
        pos = 'POSITION: {0}:{1} - {2}:{3}'.format(c_min,c_sec,l_min,l_sec)
        print(pos)

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

