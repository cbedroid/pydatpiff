import subprocess 
import psutil
from mutagen.mp3 import MP3
from ..config import Threader




class Popen(subprocess.Popen):
    registered_popen = []

    def __init__(self,*args,**kwargs):
        """ build subprocess Popen object"""

        self.kill_on_start()
        kwargs['stdin']  = subprocess.PIPE
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE
        super().__init__(*args,**kwargs)    

    @staticmethod
    def kill_on_start():
        for process in psutil.process_iter():
            try:
                if 'mpv' in process.name():
                    process.terminate()
            except:
                pass


    @Threader
    def register(self,callback,*args,**kwargs):
        """
        Kills subprocess Popen when error occur or when 
        process job finish"""
        self.registered_popen.append(self) 
        while True:
            if self.poll() is not None:
                callback(*args,**kwargs)
                self.kill()
                break
    

    @classmethod
    def unregister(cls):
        """Unregister and terminate Popen process"""
        for popen in cls.registered_popen:
            popen.kill()
        cls.registered_popen = []


    @property
    def is_running(self):
        if self.poll() is None:
            return True
        return False


class MetaData(MP3):
    def __init__(self,track):
        super().__init__(track)


    @property
    def trackDuration(self):
        return self.info.length



           



