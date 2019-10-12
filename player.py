import re
import vlc 
import threading 
import signal 
from time import sleep

class PlayerError(Exception):

    @staticmethod
    def error_msg(key,exceptions=None):
        errors= {'Instance':'VLC can not initailize. Please check if your device supports vlc\n'  }
        msg = '\n'+ str(errors.get(key) or '') 
        if exceptions: 
            msg+= str(exceptions)
        return msg


class Player(object):

    def __init__(self):
        try:
            self._vlc = vlc.Instance('-q')
            self._player = self._vlc.media_player_new()
        except Exception as e:
            msg = PlayerError.error_msg('Instance') + e
            #raise PlayerError(msg)
        

    @property
    def player(self):
        return self._player

    @property
    def pause(self):
        self.player.pause()

    property
    def _format_time(self,pos):
        mins = int(pos/60000)
        secs = int((pos%60000)/1000)
        return mins,secs

    def play(self,media=None):
        ''' Play media song'''
        playing = True if self.player.is_playing() >=1 else False

        if playing:
            self.player.pause()

        if not media and self._state == 'Paused':
            self.player.pause()
            return

        elif media:
            self.player.set_mrl(media)
            self._player.play()
            self._media_length = self.player.get_length()
        else:
            print('No media to play')
        

    @property
    def info(self):
        if self._state == 'No Media':
            return 'No media' 
        c_min,c_sec = self._format_time(self.player.get_time())
        c_sec = c_sec if len(str(c_sec)) >1 else str(c_sec).zfill(2) 

        l_min,l_sec = self._format_time(self.player.get_length())
        l_sec = l_sec if len(str(l_sec)) >1 else str(l_sec).zfill(2) 
        print('MODE:',self._state)
        print('POSTITION: {0}:{1} of {2}:{3}'.format(c_min,c_sec,l_min,l_sec))
             
        
    @property
    def _state(self):
        state = re.match(r'[\w.]*\.(\w*)',str(self.player.get_state())).group(1)
        state = 'No Media' if state =='NothingSpecial' else state
        return state


    @property
    def pause(self):
        self.player.pause()

    def rewind(self,pos=10):
        '''Rewind media 
             vlc time is in milliseconds
             @params: pos:: time(second) to rewind media. default:10(sec)
        '''
        self._ffwd_rewind(pos,True)

    def ffwd(self,pos=10):
        '''Fast forward media 
             vlc time is in milliseconds
             @params: pos:: time(second) to rewind media. default:10(sec)
        '''
        self._ffwd_rewind(pos,False)


    def _ffwd_rewind(self,pos=10,rew=True):
        if self._state == 'No Media':
            return 

        if rew: 
            to_postion = self.player.get_time() - (pos * 1000)
        else:
            to_postion = self.player.get_time() + (pos * 1000)

        self.player.set_time(to_postion)
        

        
    


