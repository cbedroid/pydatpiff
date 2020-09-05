from .mpvplayer import MPV
from .vlcplayer import VLCPlayer
from ...errors import PlayerError, InstallationError
from .androidplayer import Android, AndroidError
from ..config import Datatype


class Player:
    @classmethod
    def getPlayer(cls, *args, **kwargs):
        player = kwargs.get("player", None)

        players_selection = {"vlc": VLCPlayer, "mpv": MPV, "android": Android}

        try:
            if player:
                player = Datatype.strip_lowered(player)
                chosen = players_selection.get(player)
                if chosen:
                    return chosen()
        except Exception as e:
            extended_msg = (
                "\nThe player you choosen" " is not compatible with your device.\n"
            )
            raise PlayerError(5, extended_msg)

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

        raise InstallationError(1, MediaError, _extra)
