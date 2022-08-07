from pydatpiff.errors import InstallationError, PlayerError
from pydatpiff.utils.utils import Object

from .mpvplayer import MPV
from .vlcplayer import VLCPlayer


class Player:
    @classmethod
    def getPlayer(cls, player=None):

        player_options = {"vlc": VLCPlayer, "mpv": MPV}
        # return the player specified by the user
        try:
            if player:
                player = Object.strip_and_lower(player)
                selected_player_class = player_options.get(player, None)
                if selected_player_class:
                    # return initialized player class
                    return selected_player_class.__call__()
        except:
            extended_msg = "\nThe player you have chosen is not compatible with your device.\n"
            raise PlayerError(5, extended_msg)

        # if no player is specified by the user, then select a default player
        return cls._getDefaultPlayer()

    @classmethod
    def _getDefaultPlayer(cls):
        # Note: Player order will be respected!
        default_players = [MPV, VLCPlayer]
        for player in default_players:
            try:
                return player.__call__()
            except:  # noqa
                pass

        raise InstallationError(1)
