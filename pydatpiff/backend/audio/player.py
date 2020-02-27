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
            return VLCPlayer()
        except PlayerError as e:
            print(e)


        try:
            print('trying Android')
            #android player 
            return Android()
            print('player-player:',player)
        except Exception as e:
            print('ANDROID EE:',et)

        #raise PlayerError(1,'NO player has been found')
        raise TypeError('NO player has been found')

