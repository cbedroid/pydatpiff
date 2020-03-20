import re
from .webhandler import MediaScrape
from ..urls import Urls
from ..utils.request import Session,requests
from ..errors import AlbumError


class EmbedPlayer():
    def __new__(cls,*args,**kwargs):
        if not hasattr(cls,'_session'):
            cls._session = Session()
        return super(EmbedPlayer,cls).__new__(cls)

    def __init__(self,link):
        self.link = ''.join((Urls.url['album'] ,link))


    @property
    def mix_link_response(self):
        """
        Return the requests response from the current Mixtapes link
            See __init__ or mixtapes.Mixtapes.links.
        """
        # we dont have to worry about recalling this requests method
        # multiple times,because the session will return the cache response if
        # the response has already been downloaded 

        response = self._session.method('GET',self.link)
        if response:
            return response.text
        return " "
        
    @property
    def uploader(self):
        return MediaScrape.getUploader(self.mix_link_response)

    @property
    def bio(self):
        return MediaScrape.getBio(self.player_response.text)


    @property
    def getAlbumName(self):
        text = self.player_response.text
        return re.search(r'title">(.*[\w\s]*)\</div',text).group(1)


    @property
    def album_ID(self):
        """Album ID Number  """
        return MediaScrape.get_suffix_number(self.link)


    @property
    def create_player_url(self):
        """Creates a url link to Datpiff album's media player."""
        ref_number = self.album_ID
        return  "".join(('https://embeds.datpiff.com/mixtape/', 
                                str(ref_number),
                                '?trackid=1&platform=desktop'))

    @property
    def player_response(self):
        """Return the response content of the embedUrl. SEE: embedUrl"""
        try:
            response = self._session.method('GET', self.create_player_url)
        except:
            raise AlbumError(2)
        return response


    
class Mp3():
    def __init__(self,response):
        """
        Mp3 extracts and creates audio data.

        :param: response - EmbedPlayer requests.response
                        (see EmbedPlayer)
        """
        self.response = response


    def __len__(self):
        if self.songs:
            return len(self.songs)
        return 0


    def __str__(self):
        """
        Requests response text from Embed Player response

        See: EmbedPlayer.create_player_url.
        """
        try:
            return self.response.text
        except:
            #Not a requests object
            raise Mp3Error(2)


    @property
    def song_duration(self):
        """Duration of songs"""
        return MediaScrape.get_duration_from(str(self))


    @property
    def songs(self):
        """Songs from mixtape album."""
        return MediaScrape.find_song_names(str(self))


    @property
    def urlencode_track(self):
        """
        Url encodes all mp3 songs' name 
        Each song will be prefix with its track index and url encoded.

        return: - A list of url encoded songs. 
                return datatype: list
        Ex:-02) - Off the Wall.mp3' -->  02)%20-%20Off%20the%20Wall.mp3
        """
        return MediaScrape.get_mp3_title(str(self))


    @property
    def embedPlayerID(self):
        """
        Media Album reference ID number 
        Ex: 6/m1393dba
        """
        try:
            return MediaScrape.embed_player_ID(str(self))
        except:
            Mp3Error(1)


    @property
    def mp3Urls(self):
        mp3 = []
        prefix = 'https://hw-mp3.datpiff.com/mixtapes/'
        for track in self.urlencode_track:
            endpoint = '{}{}'.format(self.embedPlayerID,track)
            yield ''.join((prefix,endpoint))

            
