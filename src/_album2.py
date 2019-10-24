import re
from .urls import Urls
from .utils.request import Session
from .utils.parser import Reparse
from .errors import AlbumError

#Change album to just get start url response embed url response
class Album():
    def __init__(self,name,link):
        self.link = ''.join((Urls.url['album'] ,link))
        self._name = name 
        self._session = Session()
    
    @property 
    def name(self):
        return self_name
    @property
    def response(self):
        response = self._session.method('GET',self.link)
        return response
   
    @property
    def ID(self):
        """Album ID Number  """
        return Reparse.get_end_digits(self.link)


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
    def songs(self):
        return Reparse.to_songs(self.response.text)


    @property
    def media_id(self):
        try:
            return re.search('/mixtapes/([\w\/]*)', self.response.text).group(1)
        except:
            AlbumError(1)

    @property
    def mp3Urls(self):
        urls = re.findall(r'meta\scontent\="(//[\w/?].*)"\sitemprop', self.response.text)
        if not urls:
            raise Mp3Error(2)
        https = [''.join(('https',url)) for url in urls]

        #make the all mp3 urls 
        mp3 = []
        prefix = 'https://hw-mp3.'
        for index,song  in enumerate(self.songs,start=1):
            data = ['datpiff.com', self.media_id,
                     str(index).zfill(2), Reparse.encodeMp3(song)]
            endpoint = '{}/mixtapes/{}/{}%20-%20{}.mp3'.format(*data)
            mp3.append(''.join((prefix,endpoint)))

        if not mp3:
            raise Mp3Error(1)
        return mp3

            


