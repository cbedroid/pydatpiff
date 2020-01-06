import re
import vlc 
from .frontend.display import Print
from time import sleep
from .errors import PlayerError


class Player(object):
    """Media player controller""" 

    def __init__(self):
        try:
            self._vlc = vlc.Instance('-q')
            self._player = self._vlc.media_player_new()
        except Exception as e:
            extended_msg = 'Please check if your device supports VLC'
            raise PlayerError(1,extended_msg)

        self._track_set = False
        self.song = None
   

    def _seeker(self,pos=10,rew=True):
        if self._state == 'No Media':
            return 
        if rew: 
            to_postion = self.player.get_time() - (pos * 1000)
        else:
            to_postion = self.player.get_time() + (pos * 1000)
        self.player.set_time(to_postion)


    @property
    def player(self):
        return self._player
    

    @property
    def _state(self):
        """Current state of the song being played"""
        state = re.match(r'[\w.]*\.(\w*)',str(self.player.get_state())).group(1)
        state = 'No Media' if state =='NothingSpecial' else state
        return state

       

    def setTrack(self,song,media=None):
        if  media:
            self.song = song
            self.player.set_mrl(media)
            self._track_set = True
        else:
            Print('No media to play')
        

    property
    def _format_time(self,pos):
        """Format current song time to clock format"""
        mins = int(pos/60000)
        secs = int((pos%60000)/1000)
        return mins,secs

    

    @property
    def info(self):
        """Returns feedback for media song being played"""
        if self._state == 'No Media':
            return 'No media' 
        c_min,c_sec = self._format_time(self.player.get_time())
        c_sec = c_sec if len(str(c_sec)) >1 else str(c_sec).zfill(2) 

        l_min,l_sec = self._format_time(self.player.get_length())
        l_sec = l_sec if len(str(l_sec)) >1 else str(l_sec).zfill(2) 
        
        Print('TRACK:',self.song)
        Print('MODE:',self._state)
        pos = 'POSITION: {0}:{1} - {2}:{3}'.format(c_min,c_sec,l_min,l_sec)
        Print(pos)
             

    @property
    def _current_volume(self):
        """ Current media player volume"""
        return self.player.audio_get_volume()


    def _set_volume(self,vol=5,way='down'):
        """Turn the media volume up or down"""
        if isinstance(vol,(int,str)):
            if not str(vol).isnumeric():
                return 

            vol = int(vol)
            min_vol = 0
            max_vol = 100
            try:
                current_volume = int(self._current_volume)
                if way == 'down':
                    if current_volume - vol < min_vol:
                        vol = min_vol 
                    else:
                        vol = current_volume - vol
                elif way == 'up':
                    if current_volume + vol > max_vol:
                        vol = max_vol
                    else:
                        vol = current_volume + vol
                elif way == 'exact':
                    vol = 0 if vol < min_vol else vol 
                    vol = 100 if vol > max_vol else vol
                Print('volume: %s'%vol)
            except:
                pass
        self.player.audio_set_volume(vol)


    def volumeUp(self,vol=5):
        """Turn the media volume up"""
        self._set_volume(vol,way='up')
     

    def volumeDown(self,vol=5):
        """Turn the media volume down"""
        self._set_volume(vol,way='down')


    def volume(self,vol=None):
        """Set the volume to exact number"""
        if vol is None:
            return
        self._set_volume(vol,way='exact')
 
   
    @property
    def play(self):
        """ Play media song"""
        playing = True if self.player.is_playing() >=1 else False

        if playing:
            # call play while playing ,them pause 
            self.player.pause()
        elif self._state == 'Paused':
            self.player.pause()

        elif self._track_set:
            self.player.play()
            self._track_set = False
        return


   
    @property
    def pause(self):
        """Pause the media song"""
        self.player.pause()


    def rewind(self,pos=10):
        """
        Rewind the media song
             vlc time is in milliseconds
             @params: pos:: time(second) to rewind media. default:10(sec)
        """
        self._seeker(pos,True)


    def ffwd(self,pos=10):
        """Fast forward media 
             vlc time is in milliseconds
             @params: pos:: time(second) to rewind media. default:10(sec)
        """
        self._seeker(pos,False)


       
    @property
    def stop(self):
        self.player.stop()


    def close(self):
        self.stop

      
     
