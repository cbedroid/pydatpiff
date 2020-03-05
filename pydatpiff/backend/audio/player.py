import traceback
from .androidplayer import Android, AndroidError
from .vlcplayer import VLCPlayer
from ...errors import PlayerError

class Player:
    @classmethod
    def getPlayer(cls,*args,**kwargs):
        player = None
        try:
            return VLCPlayer()
        except:
            pass

        try:
            return Android()
        except:
            pass

        raise TypeError('NO player has been found')

