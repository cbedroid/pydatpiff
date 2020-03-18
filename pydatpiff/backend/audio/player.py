import traceback
from .androidplayer import Android, AndroidError
from .vlcplayer import VLCPlayer
from .mpvplayer import MPV
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
            return MPV()
        except Exception as e:
            pass


        try:
            return MPV()
        except Exception as e:
            pass

        try:
            return Android()
        except:
            pass

        raise TypeError('NO player has been found')

