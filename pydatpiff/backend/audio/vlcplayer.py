import vlc
from ...errors import PlayerError


class VLCPlayer():
    def __init__(self,*args,**kwargs):
        try:
            self._vlc = vlc.Instance('-q')
            self._player = self._vlc.media_player_new()
        except Exception as e:
            print('VLC: ',e)
            #extended_msg = 'Please check if your device supports VLC'
            #raise PlayerError(1,extended_msg)
        self._is_track_set = False
        self.song = None


    @property
    def _state(self):
        """Current state of the song being played"""
        state = re.match(r'[\w.]*\.(\w*)',str(self._player.get_state())).group(1)
        state = 'No Media' if state =='NothingSpecial' else state
        return state

    def setTrack(self,name,song=None):
        if  song:
            self._player.set_mrl(song)
            self._is_track_set = True
        else:
            Print('No media to play')


    def _set_volume(self,vol=5,way='down'):
        """Turn the media volume up or down"""
        if isinstance(vol,(int,str)):
            if not str(vol).isnumeric():
                return 

            vol = int(vol)
            min_vol = 0
            max_vol = 100
            try:
                current_volume = int(self._volumeLevel)
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
        self._player.audio_set_volume(vol)



    @property
    def _volumeLevel(self):
        """ Current media _player volume"""
        return self._player.audio_get_volume()


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
    def track_time(self):
        return self._player.get_time()

    @property
    def track_size(self):
        return self._player.get_length()


    def _format_time(self,pos=None):
        """Format current song time to clock format"""
        mins = int(pos/60000)
        secs = int((pos%60000)/1000)
        return mins,secs

   
    @property
    def play(self,*args,**kwarg):
        """ Play media song"""
        if self.state['playing']:
            # pause if track is already playing
            self.pause
        else:
            self._is_track_set = True
            self._player.play()
        return


    @property
    def pause(self):
        """Pause the media song"""
        self._player.pause()
     
    def _seeker(self,pos=10,rew=True):
        if self._state == 'No Media':
            return 
        if rew: 
            to_postion = self._player.get_time() - (pos * 1000)
        else:
            to_postion = self._player.get_time() + (pos * 1000)
        self._player.set_time(to_postion)



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
        self._player.stop()

