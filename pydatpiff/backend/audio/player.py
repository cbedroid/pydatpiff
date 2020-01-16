from .androidplayer import Android, AndroidError
from .vlcplayer import VLCPlayer
from .base import BasePlayer
from ...errors import PlayerError

class Player():

    @classmethod
    def getPlayer(cls,*args,**kwargs):
        print('\nBEGINNING')
        try:
            #vlc player 
            #self.player = VLCPlayer(*args,**kwargs)
            return VLCPlayer(*args,**kwargs)
        except PlayerEror:
            print('VLC PLAYER PASS')

        try:
            #vlc player 
            print('TRYING ADROID')
            return AndroidPlayer(*args,**kwargs)
        except:
            print('Android PLAYER PASS')

        raise TypeError('NO player has been found')







        

