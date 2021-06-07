from pydatpiff.backend.utils import Object
from pydatpiff.errors import InstallationError, PlayerError

from .androidplayer import Android
from .mpvplayer import MPV
from .vlcplayer import VLCPlayer


class Player:
    @classmethod
    def getPlayer(cls, *args, **kwargs):
        player = kwargs.get("player", None)

        players_selection = {"vlc": VLCPlayer, "mpv": MPV, "android": Android}

        try:
            if player:
                player = Object.strip_and_lower(player)
                chosen = players_selection.get(player)
                if chosen:
                    return chosen()
        except:
            extended_msg = (
                "\nThe player you choosen"
                " is not compatible with your device.\n"
            )
            raise PlayerError(5, extended_msg)

        try:
            return VLCPlayer()
        except:
            pass

        try:
            return MPV()
        except:
            pass

        try:
            return Android()
        except:
            pass

        raise InstallationError(1)
