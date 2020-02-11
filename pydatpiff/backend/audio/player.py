import traceback
from .androidplayer import Android, AndroidError
from .vlcplayer import VLCPlayer
from ...errors import PlayerError

class Player:
    @classmethod
    def getPlayer(cls,*args,**kwargs):
        player = None
        try:
            #vlc player 
            print('trying vlc')
            player =  VLCPlayer()
        except PlayerError:
            pass

        try:
            print('trying Android')
            #android player 
            player = Android()
            print('player-player:',player)
        except Exception as e:
            print('ANDROID EE:',et)

        return player
        #raise PlayerError(1,'NO player has been found')
        raise TypeError('NO player has been found')

