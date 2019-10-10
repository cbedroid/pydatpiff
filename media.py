import os
import re
import math
import platform
import threading
from player import Player
from Request import Session
from convert import Convert

def converter(file_size):
    if file_size == 0:
        return '0B'
    
    size_name = ['B','KB','MB','GB','TB','PB','EB','ZB','YB']
    change = int(math.floor(math.log(file_size,1024)))
    power = math.pow(1024,change)
    result = round(file_size / power,2)
    return '%s %s'%(result,size_name[change])
 

class Media(Session):
    ''' Media player that control the songs selected from Mixtapes ''' 
    def __new__(cls,*args,**kwargs):
        system = platform.system()
        if system == 'Linux':
            cls.tempfile ="/sdcard/sample.mp3"
        elif system == 'Windows':
            tempfile = os.environ.get('tempfile') or ''
            cls.tempfile = tempfile +  "/sample.mp3"
        else:
            cls.temp = 'sample.mp3'
        return super(Media,cls).__new__(cls)

    def __str__(self):
        return "%s(%s('hot'))"%(self.__class__.__name__,self._get_media.__name__)

    def __repr__(self):
        pass
        #return 'Media(%s)'%(self._get_media.__name__)


    def __init__(self, mixtape=None):
        print('Media initailize')
        if not mixtape:
            print('Mixtapes object must be pass to Media')
            raise ValueError()
        self._get_media = mixtape
        #self.session = requests.Session()
        self._artist_name = None
        self._title_name = None
        self.album_link = None
        self._song_index = None
        self._selected_song = None
        self._isWindows = platform.system() == 'Windows'
        self._isLinux =  platform.system() == 'Linux'
        self.Convert = Convert()
        self.soup =None
        self._downloaded_song = None

        super(Media, self).__init__()

    def setMedia(self, selection):
        '''Setup the media player and queue artist
        
        '''
        choice = self._get_media._select(selection)
        if not choice:
            print("Media is not set!\n-->\tIncorrect Value: %s" % selection)
            return
        self._artist_name = self._get_media.artists[choice[1]]
        self._title_name = self._get_media.titles[choice[1]]
        self.album_link = "http://www.datpiff.com"+choice[0]
        self._get_songs()
        self._player_links()

        
    def _threader(f):
        @wraps(f)
        def inner(self,*a,**kw):
            print('\nStart Threading')
            fun = f(self,*a,**kw)
            t= threading.Thread(target=funct,args=(a,),kwargs=kw)
            t.daemon = True
            t.start()
            return t
        return inner

    @property
    def artist(self):
        return self._artist_name


    @artist.setter
    def artist(self, name):
        self.setMedia(name)


    @property
    def title(self):
        return self._title_name


    @title.setter
    def title(self, name):
        self.setMedia(name)


    @property
    def songs(self):
        if hasattr(self,'_songs'):
            return self._songs


    def _get_songs(self):
        if not self.album_link:
            print("You have to set Media first ")
            return None

        web_link = "https://www.datpiff.com/" + self.album_link
        response = self.method('GET',web_link)
        print('Response:',response)
        status = response.status_code
        print('songs link:',web_link)
        if status != 200:
            print("No Media data available")
            return 
        text = response.text
        songs = re.findall(r'li[\s*].*title="(.*[\w\s]*)">',text)
        self._songs = songs
        return songs

    @property
    def show_songs(self):
        try:
            songs = self.songs
            [print('%s: %s'%(a+1,b)) for a,b in enumerate(songs)]
        except TypeError:
            print("Please set Media first\nNo Artist name")

    @property
    def song(self):
        return self._selected_song

    @song.setter
    def song(self, name):
        self._song_index = None
        songs = self.songs
        length = len(songs)
        if isinstance(name, (int)):
            if name > length:
                name = length
                self._selected_song = songs[name-1]
                self._song_index = name-1
            elif name == 0:
                name = 1

            if name <= length:
                self._selected_song = songs[name-1]
            self._song_index = name-1
        else:
            songs = [s.lower().strip()
                     for s in songs]  # use to ignore case
            name = name.lower().strip()
            songchoice = [[n, songs[n]]
                          for n, s in enumerate(songs) if name in s]
            if songchoice:
                self._song_index, self._selected_song = songchoice[0]
            else:
                print("Invalid song name ")
                self._song_index = None
                self._selected_song = None
        if self._selected_song:
                print(self._selected_song)

    @property
    def _song_link(self):
        if self._song_index is None:
            print('\n-- Media.song not set. Set "Media.song" to get mp3 link --')
            return None
        return self.mp3Links[self._song_index]

    @property
    def mp3Urls(self):
        return self._make_mp3_url()

    @property
    def mp3Links(self):
        if hasattr(self,'_mp3_links'):
            return self._mp3_links

    @mp3Links.setter
    def mp3Links(self,*args):
        self._player_links()

    def _player_links(self, path=None):
        '''Get the raw mp3 link and convert them to https format''' 
        if not self.album_link:
            return
        response = self.method('GET',self.album_link)
        if response.status_code == 200:
            text = response.text
            links = re.findall(r'meta\scontent\="(//[\w/?].*)"\sitemprop', text)
            if links:
                links = ['https:'+link for link in links]
                self._mp3_links = links
                return links
        else:
            print("\nBad album link:", self.album_link)


    def _make_mp3_url(self,*args,**kwargs):
        #track=None,index = None):
        #def buildlink(self)

        tid = self.mp3Links
        pd = [re.search(r'(d[\w.]*)/player/(m\w*)\?.*=(\d*)',link) for link in tid]
        urls =[]
        for part ,song in zip(pd,self.songs):
            data =  [part[1],part[2],part[3].zfill(2),re.sub(' ','%20',song)]
            urls.append('https://hw-mp3.{}/mixtapes/9/{}/{}%20-%20{}.mp3'.format(*data))
        return urls
        

    def play(self,number = None, full=False):
        t=threading.Thread(target =self._sample,args=(number,full))
        t.daemon = True
        t.start()
        print("\nPLAYING DEMO THREAD")


    def _sample(self, track=None, full_song=False):
        song_length = len(self.songs)
        links = self.mp3Urls
        _index = None
        selection = None

        if track:
            if isinstance(track,int) or track.isdigit():
                _index = int(track) - 1
                # check if _index in range
                if _index > song_length:  
                    _index =  song_length - 1 
                elif _index < 0:
                    _index = 0
            elif isinstance(track,str):
                track = track.lower().strip() 
                # check if the song in songlist
                tmp = [s for s in self.songs\
                        if track  in s.lower().strip()
                      ]

                if tmp:
                    if len(tmp) > 1:
                        # select the first song index 
                        print('\nMultiple songs with "%s" found '%track) 
                        _index = self.songs.index(tmp[0])+1
                    else:
                        tmp = ''.join(tmp)
                        _index = self.songs.index(tmp)+1
                else:
                    print('\nNo song found ')
                    return None

            if _index:
                print('\nPreparing request')
                link =  links[_index]
                print('LINK: ',link)
            else:
                print('\nNo request to make')

        else: # If no parameter enter
            if self.song:
                _index = self._song_index
                link = links[_index]
            else:
                print("\nNo song was set\nset 'Media.song' first")
                return

        # Write songname to file
        if link:
            songname = self.songs[_index]
            with open(self.tempfile, "wb") as ws:
                data = self.session.get(link)
                content = data.content
                if data.status_code == 200:
                    song_length = len(content)
                    if  full_song: # demo whole song
                        print("\t\t--- Demo whole song ---")
                        chunk = content
                    else: # demo partial song
                        samp = int(song_length/5)
                        start = int(samp/5)
                        print("\nSample size:",converter(samp))
                        chunk = content[start:samp+start]
                    ws.write(chunk)
                    print("\nPlaying Sample:",self.artist,songname)
                    self.player = Player()
                    self.player.play(self.tempfile)

                else:
                    print("Error saving songname web-status-error")




    def __sample_old(self,track=None, full=False):
        # NOT USED
        songs_length = len(self.songs)
        links = self.mp3Links
        queued = None
        
        
        # Check for numbers enter
        if track:
            if isinstance(track,int) or track.isdigit():
                queued = int(track)
                # Check if songname length out of range
                if track > songs_length:
                    index_ = songs_length
                    queued = links[songs_length]
                else:
                    print("Track in range")
                    index_ = int(track)-1
                    queued = links[queued-1]
            else:
                if isinstance(track,str):
                    tmp = [ songname for songname in self.songs\
                            if track.lower().strip() in songname.lower().strip()]
                    if tmp:
                        if len(tmp) > 1:
                            print("\nMultiple tracks found")
                            # Multiple found, just get the first track then
                            index_ = self.songs.index(tmp[0])
                            try:
                                queued= links[index_]
                            except:
                                print("\nNo song queued")
                                return

                        else: # one track found
                            tmp = "".join(tmp)
                            index_ = self.songs.index(tmp)
                            queued= links[index_-1]


                    else:
                        print("\n No song found")
                        return 

            link = self._make_mp3_url(track=queued,index=index_)
            songname = self.songs[index_]
        else:
            link = self.mp3Urls
            songname = self.song

        print("Maker link",link)
        print(f'\nIndex: {index_}\nQueued: {queued}')
        sleep(1)

        # Write songname to file
        with open(self.tempfile, "wb") as ws:
            data = self.session.get(link)
            content = data.content
            if data.status_code == 200:
                song_length = len(content)
                if  full: # demo whole song
                    print("\t\t--- Demo whole song ---")
                    chunk = content
                else: # demo partial song
                    samp = int(song_length/5)
                    start = int(samp/5)
                    print("\nSample size:",converter(samp))
                    chunk = content[start:samp+start]
                ws.write(chunk)
                print( "\nPlaying Sample:",songname)
                self.player = Player()
                self.player.play(self.tempfile)
                '''
                try:
                    while player.poll() is None:
                        #self.player.stdin.write(bytes(input(" "),"ascii"))
                        if player.poll() is not None:
                            print("\nSample Done")
                            break
                    os.system("rm %s"%self.tempfile)
                    os.system('pkill -9 mpv')
                except KeyboardInterrupt:
                    print('\nCleaning up..')
                    os.system("rm %s"%self.tempfile)
                    os.system('pkill -9 mpv')
                '''
            else:
                print("Error saving songname web-status-error")


    #@_threader
    def download(self,track_no=False,location="" ,name=None):
        if track_no and isinstance(track_no,(str,int)):
            try:
                if int(track_no) > len(self.songs):
                    track_no = len(self.songs)
                track_no = int(track_no)-1
            except Exception as e:
                print(e)

            album_song = self.mp3Links[track_no]
            if album_song: 
                link = self._make_mp3_url(track=album_song,index=track_no)
                song = self.songs[track_no-1]
            else:
                print('\nInvalid track index: %s',track_no)
                return 
        elif name: # Custom Songname
            song = name
        else:
            link = self.mp3Urls
            song = self.song

        songname = location  + self.artist + " " + song.strip()+".mp3"
        with open(songname, "wb") as ws:
            data = self.session.get(link)
            if data.status_code == 200:
                ws.write(data.content)

                if not location or not os.path.isdir(location):
                    location = os.getcwd()
                print("\n\t\t-- SONG SAVED --\n", "DIRECTORY: ",location,
                        '\nSONGNAME: ',songname,'\nSIZE:  ',converter(len(data.content)))
            else:
                print("Error saving song Non-200 status")
        #self._downloaded_song = songname
        return songname

    #@_threader
    def download_album(self,location=None):
        if location:
            if not os.path.isdir(location):
                location= ''
        else:
            location = '' 

        fname = location + "\\"+self.artist + "-" + self.title
        if not os.path.isdir(fname):
            os.mkdir(fname)
        for num, song in enumerate(self.songs):
            with open(fname+"\\"+song+'.mp3', "wb") as aw:
                self.song = num+1
                data = self.session.get(self.mp3Urls)
                if data.status_code == 200:
                    print("Saving: %s.  %s" % (num, song))
                    aw.write(data.content)
        print("\n%s album saved" % self.artist)

    


