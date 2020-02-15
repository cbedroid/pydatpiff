import os
import sys
import eyed3
from threading import Thread
from functools import wraps
from time import time
from subprocess import Popen,PIPE


class Testpiff():
    TMP = '/sdcard/2chainz.mp3'
    mp3file = '/sdcard/testmp3.mp3'
    _isplaying=False
    loaded = False
    _position = 0
    _elapse = 0

    def __init__(self):
        self.eyed3 = eyed3.load(self.TMP)
        self.totaltime = self.eyed3.info.time_secs
    
    def __len__(self):
        return len(self.content)

    def __startClock(self): 
        t = Thread(target=self.clock)
        t.daemon= True
        t.start()

            
    def Threader(f):
        @wraps(f)
        def inner(self,*a,**kw):
            t = Thread(target=f, args=(self,*a,))
            t.daemon = True
            t.start()
            return t
        return inner
   
    @property
    def isplaying(self):
        try:
            return self._isplaying
        except:
            print('isplaying Error')
            self._isplaying = False
            return False

    @isplaying.setter
    def isplaying(self,val):
        self._isplaying = val


    def clock(self):
        print('\nClock started')
        start = time()
        while True:
            if self.isplaying:
                self.elapse = time() - self.start_time
            if time() - start > 3:
                #print('TIME:',self.position)
                start = time()

    @property
    def bytes_per_sec(self):
        return len(self)/self.totaltime
        
    
    def setTrack(self,song=None):
        self.loaded = False
        self._position = 0
        song = song if os.path.isfile(song) else self.TMP
        with open(song,'rb') as tmp:
            self.content = tmp.read()



    @property
    def position(self):
        pos = self._position + self.elapse
        return pos if pos > 0 else 0 

    @position.setter
    def position(self,pos):
        self._position = pos

 
    @property
    def elapse(self):
        return self._elapse

    @elapse.setter
    def elapse(self,val=0):
        self._elapse = (time() - self.start_time )


   
    def load(self,trackspot):
        #spot in seconds
        with open(self.mp3file,'wb') as mp3:
            spot = int(self.position+trackspot) 
            topos = spot*self.bytes_per_sec if spot > 0 else 1*self.bytes_per_sec
            topos = int(topos)
            print("\nSpot:",int(self.position))
            self._position = self.position + trackspot
            self.start_time = time()
            print('\nloaded to:',topos)
            mp3.write(self.content[topos:])

            """
            if not self.isplaying and not self.loaded:
                print('fresh start playing from beginning')
                self.start_time = time() + self.elapse
            else:
                self.start_time = (time() - self.start_time) + (self.elapse + spot) 
            """
            self.loaded = True
        

    @Threader
    def play(self,spot=1):
        if not self.loaded:
            self.start_time = time()
            self.__startClock()
            self.loaded = True

        self.load(spot)
        start = "am start --user 0 -a android.intent.action.VIEW -d file:///%s -t audio/*"%self.mp3file
        Popen(start,shell=True,stdin=PIPE,
                    stdout=PIPE,stderr=PIPE)
        self.isplaying = True
        start = time()
        #while time() - start <25:
        #    pass
        #self.stop

    @property
    def stop(self):
        service = "am stopservice "
        cmd = service + "org.videolan.vlc/org.videolan.vlc.PlaybackService"
        results = Popen(cmd,shell=True,stdout=PIPE,stderr=PIPE)
        self.isplaying = False

        #comment out for testing
        #self.loaded = False

if __name__  == '__main__':
    mp3 = Testpiff()

