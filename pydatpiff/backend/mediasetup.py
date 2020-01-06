import re
from .webhandler import Html
from ..urls import Urls
from ..utils.request import Session
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
        text = self.embed_response.text
        return re.search(r'title">(.*[\w\s]*)\</div',text).group(1)


    @property
    def ID(self):
        """Album ID Number  """
        return Html.get_end_digits(self.link)


    @property
    def embed_url(self):
        """Creates a url link to Datpiff album's media player."""

        ref_number = self.ID
        embed_link = "".join(('https://embeds.datpiff.com/mixtape/', 
                                str(ref_number),
                                '?trackid=1&platform=desktop'))
        return embed_link


    @property
    def embed_response(self):
        """Return the response content of the embedUrl. SEE: embedUrl"""
        try:
            response = self._session.method('GET', self.embed_url)
        except:
            raise AlbumError(2)
        return response


    
class Mp3():
    def __init__(self,response):
        self.response = response


    def __len__(self):
        if self.songs:
            return len(self.songs)


    @property
    def content(self):
        """Requests response from album url link See: Album.embed_url."""
        try:
            return self.response.text
        except:
            #Not a requests object
            raise Mp3Error(2)


    @property
    def song_duration(self):
        """Duration of songs"""
        return Html.get_duration_from(self.content)


    @property
    def songs(self):
        """Songs from mixtape album."""
        return Html.find_song_names(self.content)


    @property
    def prefix_tracks(self):
        """
        Track prefix song  
        Return url encoded song index joined with song name 
        Ex: 02) - Off the Wall.mp3' -->  02)%20-%20Off%20the%20Wall.mp3
        """
        return Html.find_name_of_mp3(self.content)


    @property
    def media_id(self):
        """
        Media Album reference ID number 
        
        Ex: 6/m1393dba
        """
        try:
            return Html.toId(self.content)
        except:
            Mp3Error(1)

    
    
    @property
    def mp3Urls(self):
        mp3 = []
        prefix = 'https://hw-mp3.datpiff.com/mixtapes/'
        for track in self.prefix_tracks:
            endpoint = '{}{}'.format(self.media_id,track)
            yield ''.join((prefix,endpoint))

            
