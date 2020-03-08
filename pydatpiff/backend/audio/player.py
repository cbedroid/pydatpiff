import traceback
from .androidplayer import Android, AndroidError
from .vlcplayer import VLCPlayer
from .mpvplayer import MPV
from ...errors import PlayerError

class Player:
    @classmethod
    def getPlayer(cls,*args,**kwargs):
        player = None
        """
        try:
            return VLCPlayer()
        except:
            pass
        """
        try:
            print('USING MPV PLAYER')
            return MPV()
        except Exception as e:
            print("MPV FAILED:",e)
            pass

        try:
            print('USING ANDROID PLYER')
            return Android()
        except:
            pass

        raise TypeError('NO player has been found')

