import re
from .webhandler import Html
from ..urls import Urls
from ..utils.request import Session,requests
from ..errors import AlbumError

#TODO::Change album to just get start url response embed url response

class Album():
    def __new__(cls,*args,**kwargs):
        if not hasattr(cls,'_session'):
            cls._session = Session()
        return super(Album,cls).__new__(cls)

    def __init__(self,link):
        self.link = ''.join((Urls.url['album'] ,link))

    @property
    def name(self):
        text = self.embed_player_response.text
        return re.search(r'title">(.*[\w\s]*)\</div',text).group(1)


    @property
    def endpoint_ID(self):
        """Return the album url endpoint_ID Number  """
        return Html.get_end_digits(self.link)


    @property
    def embeded_player_url(self):
        """Creates a url link to Datpiff album's media player."""

        ref_number = self.endpoint_ID
        embed_link = "".join(('https://embeds.datpiff.com/mixtape/', 
                                str(ref_number),
                                '?trackid=1&platform=desktop'))
        return embed_link


    @property
    def embed_player_response(self):
        """Return the response content of the embedUrl. SEE: embedUrl"""
        try:
            response = self._session.method('GET', self.embeded_player_url)
        except:
            raise AlbumError(2)
        return response


    
class Mp3():
    def __init__(self,embed_response):
        if not isinstance(embed_response,requests.models.Response):
            raise Mp3Error(1)
        self.response = embed_response


    def __len__(self):
        if self.songs:
            return len(self.songs)
    
    def __str__(self):
        """Return the requests response from album embed_response. See: Album.embeded_player_url."""
        try:
            return self.response.text
        except:
            #Not a requests object
            raise Mp3Error(2)


    @property
    def song_duration(self):
        """Duration of songs"""
        return Html.get_duration_from(str(self))


    @property
    def songs(self):
        """Songs from mixtape album."""
        return Html.find_song_names(str(self))


    @property
    def urlencode_tracks(self):
        """
        Url encodes all mp3 songs' name 
        Each song will be prefix with its track index and url encoded.

        return: - A list of url encoded songs. 
                return datatype: list
        Ex:-02) - Off the Wall.mp3' -->  02)%20-%20Off%20the%20Wall.mp3
        """
        return Html.find_name_of_mp3(str(self))


    @property
    def mediaReferenceNumber(self):
        """
        Media Album reference id number 
        Ex: 6/m1393dba
        """
        try:
            return Html.toId(str(self))
        except:
            Mp3Error(1)


    @property
    def mp3Urls(self):
        mp3 = []
        prefix = 'https://hw-mp3.datpiff.com/mixtapes/'
        for track in self.urlencode_tracks:
            endpoint = '{}{}'.format(self.mediaReferenceNumber,track)
            yield ''.join((prefix,endpoint))

            
