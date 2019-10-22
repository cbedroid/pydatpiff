import os
import re
import threading
from functools import wraps
import tempfile
from time import sleep
from .urls import Urls
from .player import Player
from .handler import converter
from .errors import MediaError
from .utils.request import Session
from .utils.filehandler import Tmp


class Media():
    """ Media player that control the songs selected from Mixtapes """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_tmpfile'):
            Tmp.removeTmpOnstart()
            tmp = tempfile.NamedTemporaryFile
            cls._tmpfile = tmp(suffix='_datpiff',delete=False)
        return super(Media, cls).__new__(cls)


    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self.mixtape)


    def __repr__(self):
        return 'Media(%s)' % (self.mixtape)


    def __init__(self, mixtape=None):
        """ Initialize Media 

        @@params: mixtape - Datpiff.Mixtapes object
        """
        print('Media initialized')
        if not mixtape:
            raise MediaError(1)

        self._session = Session()
        self.mixtape = mixtape
        self._artist_name = None
        self.album_name = None
        self.album_link = None
        self._song_index = None
        self._selected_song = None
        self.soup = None
        self._downloaded_song = None
        super(Media, self).__init__()


    def setMedia(self, selection):
        """
        Setup and queues Datpiff.Mixtapes ablum to media player by selection 
        Datpiff.Mixtapes artists or album name.

        @@params: selection - Datpiff.Mixtapes album's name or artist's name.
            #datatype 
            int - will return the Datpiff.Mixtape artist at that index.
            str - will search for an artist from Mixtapes.artists (default)
                  or album from Mixtapes.ablum. 
        """
        choice = self.mixtape._select(selection)
        if not choice:
            raise MediaError(2)
        self._artist_name = self.mixtape.artists[choice[1]]
        self.album_name = self.mixtape.mixtapes[choice[1]]
        self.album_link = "".join((Urls.url['album'], choice[0]))

        self._getSongs()
        self._getPlayerEndpoint()
        self._getTidsUrl()
        print('Setting Media to %s - %s' % (self.artist, self.album))



    @property
    def _albumResponse(self):
        if hasattr(self,'album_link'):
            response = self._session.method('GET',self.album_link)
            return response

    @property
    def artist(self):
        """Return the current artist name."""
        return self._artist_name


    @artist.setter
    def artist(self, name):
        """Set the current artist name."""
        self.setMedia(name)


    @property
    def album(self):
        """Return the current album name."""
        return self.album_name


    @album.setter
    def album(self, name):
        self.setMedia(name)


    @property
    def songs(self):
        """ Return all album songs."""
        if hasattr(self, '_songs'):
            return self._songs
        else:
            msg = "\nuse Media.setMedia('artist name') to set media first"
            print(msg)


    def _getSongs(self):
        """ Collect all songs from current Mixtapes album.
            Do not use use Media.songs instead.
        """
        response = self._albumResponse
        if not response:
            raise MediaError(3)

        text = response.text
        songs = re.findall(r'li[\s*].*title="(.*[\w\s]*)">', text)
        # Need to replace these below too :: Found in source file
        # replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/'/g, "&#39;").replace(/</g, "&lt;").replace(/>/g, "&gt;")A
        songs = [re.sub(r'amp;', '', x) for x in songs]
        self._songs = songs
        return songs


    @property
    def show_songs(self):
        """Pretty way to display all song names"""
        try:
            songs = self.songs
            [print('%s: %s' % (a+1, b)) for a, b in enumerate(songs)]
        except TypeError:
            print("Please set Media first\nNo Artist name")


    @property
    def song(self):
        """Returns the current song set by user."""
        return self._selected_song


    @song.setter
    def song(self, name):
        """ 
        Set current song
        @@params: name  - Media.songs name or index of Media.songs 
        """
        songs = self.songs
        index = self._parseSelection(name)
        if index is not None:
            self._selected_song = songs[index]
            self._song_index = index
        else:
            self.display('\n\t song was not found')


    @property
    def _song_link(self):
        """Current song album link"""
        if self._song_index is None:
            print('\n-- Media.song not set --',
                           '\nSet "Media.song" to get mp3 link')
            return None

        if hasattr(self, '_song_index'):
            return self._tid_urls[self._song_index]
        else:
            self._getTidsUrl()


    @property
    def mp3urls(self):
        """Returns the parsed mp3 url"""
        tid = self._tid_urls
        pd = [re.search(r'(d[\w.]*)/player/m\w*\?.*=(\d*)', link)
              for link in tid]
        urls = []
        for part, song in zip(pd, self.songs):
            song = re.sub(r'\&','amp',song) # this may need to go after below
            song = re.sub('[^\w\s()&.,]', '', song[:50].strip())
            data = [part[1], self.m_ids, part[2].zfill(
                2), re.sub(' ', '%20', song)]
            urls.append(
                'https://hw-mp3.{}/mixtapes/{}/{}%20-%20{}.mp3'.format(*data))
        return urls


    def _getPlayerEndpoint(self):
        """
        Return the embeds player endpoint

        https://www.datpiff.com/player/ --> m97454a7 <-- ?tid=1 "
        """
        player_no = re.search(r'\.(\d*)\.html',self.album_link).group(1)
        player_link = "".join(('https://embeds.datpiff.com/mixtape/', 
                                str(player_no),
                                '?trackid=1&platform=desktop'))
        try:
            response = self._session.method('GET', player_link)
            response.raise_for_status()
            text = response.text

        except Exception as e:
            print(e)
            raise MediaError('Media._Endpoint Error')
        else:
            self.m_ids = re.search(
                '/mixtapes/([\w\/]*)', text).group(1)


    def _getTidsUrl(self):
        """Get the raw mp3 link and convert them to https format"""
        response = self._albumResponse

        if not response:
            raise MediaError(2)
        text = response.text
        links = re.findall(
            r'meta\scontent\="(//[\w/?].*)"\sitemprop', text)
        if links:
            links = ['https:'+link for link in links]
            self._tid_urls = links  # capturing as a variable
            return links

       
    def _parseSelection(self, select):
        """Parse all user selection and return the correct songs
           @@params: select  - Media.songs name or index of Media.songs 
        """
        select = 1 if select == 0 else select
        songs = dict(enumerate(self.songs, start=1))

        # checking from index 
        if isinstance(select,int):
            length = len(self.songs) + 1
            if select >= 0 and select < length:
                select = 1 if select == 0 else select
                return select-1

        select = str(select).lower().strip()
        selection = list(filter(lambda x: select in x[1].lower(),(songs.items()
                            )))

        if selection:
            return (min(selection)[0]) - 1
        else:
            print('\n\t -- No song was found --')


    def _cacheSong(self, song, data):
        """
        _cacheSong - Captures the songname and content when user play
         or download a song. This prevents downloading song content twice
         when playing or downloading a song. Data from each song will be 
         stored in _song_cache for future access.
        """
        if not hasattr(self, '_song_cache'):
            self._song_cache = {}
        name = "-".join((self.artist, song))
        self._song_cache[name] = data


    def _checkCache(self, song):
        """Check if song have already been download.
        If so,requests response is return.
        """
        in_cache = '-'.join((self.artist, song))
        if hasattr(self, '_song_cache'):
            if in_cache in self._song_cache:
                response = self._song_cache[in_cache]
                return response


    def play(self, track=None, demo=False):
        """ 
        Play song (uses vlc media player) 
         @@params: track - name or index of song type(str or int)
         @@params: demo  - True: demo sample of song
                              False: play full song 
                              *default: False
        """
        selection = self._parseSelection(track)
        if selection is not None:
            link = self.mp3urls[selection]
            songname = self.songs[selection]
            self.song= selection

            # Write songname to file
            response = self._checkCache(songname)
            if response:
                content = response.content
            else:
                try:
                    # check if song already been downloaded
                    response = self._session.method('GET', link)
                    content = response.content
                    response.raise_for_status()
                except:
                    status = response.status_code
                    song = " - ".join((self.artist, songname))
                    print(
                        '\n%s song can not play. Try again ' % (song))
                    return

            track_size = len(content)
            # play demo or full song
            if not demo:  # demo whole song
                chunk = content
                samp = int(track_size)
            else:  # demo partial song
                samp = int(track_size/5)
                start = int(samp/5)
                chunk = content[start:samp+start]

            with open(self._tmpfile.name, "wb") as ws:
                ws.write(chunk)
            sorf = 'Demo' if demo else 'Full Song'
            print('\n%s %s %s' % ('-'*20, sorf, '-'*20))
            print('Song: %s - %s' % (self.artist, songname))
            print("Size:", converter(samp))

            if not hasattr(self, 'player'):
                self.player = Player()
            self._cacheSong(songname, response)
            self.player.setTrack(self._tmpfile.name)
            self.player.play


    def download(self, track=False, output="", name=None):
        """
        Download song from Datpiff
        @@params: track - name or index of song type(str or int)
        @@output: location to save the song (optional)
        @@name:   rename the song (optional)
            default will be song's name 
        """
        selection = self._parseSelection(track)
        if selection is None:
            print('\n\t No song found to download')
            return
        if os.path.isdir(output):
            location = output
        else:
            print('Invalid directory: %s'%output)
            return 
        link = self.mp3urls[selection]
        song = self.songs[selection]
        songname = '/'.join((location, self.artist +
                             " - " + song.strip()+".mp3"))
        try:
            response = self._checkCache(song)
            if response:
                content = response.content
            else:
                response = self._session.method('GET', link)
                response.raise_for_status()

            with open(songname, "wb") as ws:
                ws.write(response.content)
                print('\nSONGNAME: ', songname,
                               '\nSIZE:  ', converter(len(response.content)))
            self._cacheSong(songname, response)
        except:
            print('Cannot download song %s' % songname)


    def downloadAlbum(self, output=None):
        if not output:
            output = os.getcwd()
        elif not os.path.isdir(output):
            print('Invalid directory: %s'%output)
            return

        fname = output +'\\'+ "-".join((self.artist, self.album))
        fname = re.sub('[^A-Za-z1-9_\-\.] ', '_', fname)
        # make a directory to store all the ablum's songs
        if not os.path.isdir(fname):
            os.mkdir(fname)

        for num, song in enumerate(self.songs):
            self.download(song, output=fname)
        print("\n%s %s saved" % (self.artist, self.album))

