from .mpvplayer import MPV
from .vlcplayer import VLCPlayer
from ...errors import PlayerError
from .androidplayer import Android, AndroidError

class Player:
    @classmethod
    def getPlayer(cls,*args,**kwargs):
        player = None


        try:
            return VLCPlayer()
        except:
            pass

        try:
            return MPV()
        except Exception as e:
            pass


        try:
            return Android()
        except:
            pass

        raise TypeError('No player has been found')

