from .mpvplayer import MPV
from .vlcplayer import VLCPlayer
from ...errors import PlayerError,InstallationError
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

        """
        try:
            return Android()
        except:
            pass
        """
        raise InstallationError(1,MediaError,_extra)

