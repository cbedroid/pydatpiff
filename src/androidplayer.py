import os
import sys
import select
import atexit
import eyed3
import re
import threading 
from subprocess import PIPE,Popen,check_output
from time import time,sleep
from glob import glob
from functools import wraps

class MediaError(Exception):
    pass

class Media():
    def __init__(self,songs=None):
        if songs:
            self.songs = songs
        else:
            self.setSongs('/sdcard/*/*',ext='.mp3')
        start = "am start --user 0 -a android.intent.action.VIEW "
        self._command = start +"-d file:///sdcard/piper.mp3 -t audio/mp3"
        self._tmp = '/sdcard/piper.mp3'

    def __len__(self):
        return len(self.content)


    @property 
    def songs(self):
        """
        @Property - Return a list of songs in directory 
        Song can be set by setting 'Media.songs = directory_of_songs
        default - Android '/sdcard/' directory 
        """
            
        if hasattr(self,"_songs"):
            songs = self._songs
            self.len = len(songs)
            return songs


    def setSongs(self,songs,ext='mp3'):
        strip_dir = os.path.dirname(re.sub(r"[^w/]*","",songs))
        dirname = os.path.splitext(strip_dir)[0]
        self._songs = []
        if not os.path.isdir(dirname):
            print("\nInvalid song directory: %s"%dirname)
            return
        songs = re.search(r".*\w*(/|\\)*[^\w.]",songs).group(0)
        if "*"  not in songs:
            ext = "**."+ext
        songs =  glob('%s%s'%(songs,ext),recursive=True)
        if songs:
            self._songs = songs
        

    def _threader(f):
        @wraps(f)
        def inner(self,*a,**kw):
            t = threading.Thread(target=f,args=(self,))
            t.daemon = True
            t.start()
            return t
        return inner


    @property
    def time(self):
        """ Print the track elaspe time in human readable format"""
        tmin,tsec = self._parse_time()
        nmin,nsec = self._parse_time(self.position)
        if tmin==nmin and tsec==nsec:
            nmin="00"
            nsec="01"
        print("Track %s:%s - %s:%s"%(nmin,nsec,tmin,tsec))


    @property
    def info(self):
        """ 
        Return the information about the song.
        artist name,track name ,album name, and duration 
        """
        self._setTrackInfo()
        mins,secs = self._parse_time()
        print('\nArtist:',self.artist)
        print('Song:',self.title)
        print('Album:',self.album)
        print('Duration: %s:%s'%(mins,secs))



    def _parse_time(self,_time=None):
        """Return the elaspe time of the track in clock format """
        _time =  self.eyed3.info.time_secs if not _time else _time
        mins = int(_time/60)
        secs = int(_time%60)
        mins = str(mins).zfill(2)
        secs = str(secs).zfill(2)
        return  mins,secs


    @property
    def artist(self):
        """ Artist name"""
        if hasattr(self,"_artist"):
            return self._artist
        
    @artist.setter
    def artist(self,name):
        self._artist = name


    @property
    def album(self):
        """ Album name"""
        if self.tag:
            return self.eyed3.tag.album

    @property
    def title(self):
        """ Song name"""
        return self._title


    @title.setter
    def title(self,name):
        self._title = name


    @staticmethod
    def _splitSong(song,keep=1):
        """Parse song and split by '-' """
        if "-" in song:
            return song.split("-")[keep]
        return song
        

    def _setTrackInfo(self):
        """Set the artist name  and title of the song"""
        try:
            song = self.songs[self._index]
            title = re.sub(".mp3","",os.path.basename(song))
            self.artist = self._splitSong(title,0)
            self.title = self._splitSong(title,-1)
        except:
            tag = self.eyed3.tag.title 
            self.artist = self.eyed3.tag.artist
            self.title = self._splitSong(self.eyed3.tag.title,1)


    def _fileCheck(self,path):
        """ 
        Check if file path exists 
        @params:: path - path of song 
        """
        if os.path.isfile(self._tmp):
            os.remove(self._tmp)
        if not os.path.isfile(path):
            msg = "Song --> '%s' was  not founded"%path
            raise MediaError(msg)


    def load(self,file):
        """
        Open file path  and return its content
        @params:: file - path of the song
        """
        self.isPaused = False
        self.eyed3 = eyed3.load(file)
        self.tag = self.eyed3.tag
        f = open(file,'rb')
        self.content = f.read()
        f.close()


    @property
    def bytes_elaspe(self):
        """Current bytes of the current song"""
        return self.bytes_per_sec * self.position

    @property
    def position(self):
        """Current position of track in seconds"""
        if hasattr(self,'start_time'):
            return int(time() - self.start_time)
        return 1

    @position.setter
    def position(self,spot):
        self.start_time = time()-spot


    @property
    def bytes_per_sec(self):
        """song bytes per seconds"""
        return len(self) / self.eyed3.info.time_secs


    def _setContent(self,length):
        """Write media content to file"""
        br = self.bytes_per_sec
        length = int(br* int(self.position + length))
        if os.path.isfile(self._tmp):
            os.remove(self._tmp)
        with open(self._tmp,'wb') as _tmp:
            _tmp.write(self.content[length:])
        return length


    def play(self,song=None ,pos=1):
        """
        Play media songs

        @params:: song - song  play 
                    type:: int - index of songs  (see Media.songs)
                           str - path of the song to play 
                  pos   - play a song at the given postion (seconds)
        """
        if song:
            song = str(song)
            if song.isnumeric():
                choices = self.songs
                if not choices:
                    print("\nSongs are not set")
                    return
                index = int(song)-1 if self.len >= int(song) >= 0 else 1
                self._index = index 
                song = self.songs[index]
            else:
                self._songs = [song]
                self._index = 0

            if song:
                self._fileCheck(song)
                self.start_time = time()
                self.load(song)
                self.info

        if self.isPaused: # detect if player is paused
            # Set the pause position to the current position
            pos = self._paused_pos
            self.isPaused = False

        self._setContent(pos)
        self.player = Popen(self._command,shell=True,stdin=PIPE,
                    stdout=PIPE,stderr=PIPE)
        self.time

  
    def volume(self,vol):
        """
        Media volume controls
        @params:: vol - set the media volume range 0 - 100 
        """
        os.system('termux-volume music %s'% vol)

    
    @property
    def pause(self):
        """Pause song"""
        # capture the position the media player was pause
        if not self.isPaused:
            self.stop
            print("Pause")
            self._paused_pos = self.position
            self.isPaused = True
        else: # unpause
            self.isPaused =False
            self.position = self._paused_pos
            print("Unpause")
            self.time
            self.play()


    def _playback(self,pos=5,way=True):
        """Control fast forward and rewind function"""
        spot = pos
        if self.isPaused:
            self.position = self._paused_pos
            self.isPaused = False

        self.start_time+=spot
        self.time
        self.play(pos=pos)


    def rewind(self,pos=5):
        self._playback(pos,True)
        

    def ffwd(self,pos=5):
        self._playback(-pos,False)

    @property
    def stop(self):
        service = "am stopservice "
        cmd = service + "org.videolan.vlc/org.videolan.vlc.PlaybackService"
        results = Popen(cmd,shell=True,stdout=PIPE,stderr=PIPE)


"""
@atexit.register
def remove_file():
    removed = not os.system('rm /sdcard/piper.mp3')
    msg = 'Removed' if removed else "False"
    print(msg)


on = input('\n>> ')
"""
