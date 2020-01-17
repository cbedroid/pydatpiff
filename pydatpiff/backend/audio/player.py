import traceback
from .androidplayer import Android, AndroidError
from .vlcplayer import VLCPlayer
from ...errors import PlayerError

class Player:
    @classmethod
    def getPlayer(cls,*args,**kwargs):
        try:
            #vlc player 
            return VLCPlayer()
        except PlayerError:
            pass
        try:
            #android player 
            return AndroidPlayer()
        except:
            pass
        
        raise PlayerError(1,'NO player has been found')

