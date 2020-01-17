import traceback
from .androidplayer import Android, AndroidError
from .vlcplayer import VLCPlayer
from ...errors import PlayerError

class Player:
    @classmethod
    def getPlayer(cls,*args,**kwargs):
        print('\nBEGINNING')
        try:
            #vlc player 
            print('\nTRYING VLC')
            return VLCPlayer()
        except PlayerError:
            print('\nVLC PLAYER PASS')
            print(traceback.print_exc())

        try:
            #android player 
            print('TRYING ANDROID')
            return AndroidPlayer()
        except:
            print('Android PLAYER PASS')
            raise PlayerError(1,'NO player has been found')
        
        raise TypeError('No Audio Player was specified') 

