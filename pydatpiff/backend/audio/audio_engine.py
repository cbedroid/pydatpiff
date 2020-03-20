import os
import subprocess 
import atexit
from mutagen.mp3 import MP3
from ..config import Threader


class Popen(subprocess.Popen):
    registered_popen = []

    def __init__(self,*args,**kwargs):
        """ build subprocess Popen object"""

        self.stop_mpv()
        kwargs['stdin']  = subprocess.PIPE
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE
        atexit.register(self.kill_on_quit)
        super().__init__(*args,**kwargs)    



    @staticmethod
    def _pid_of_mpv():
        player = subprocess.check_output('pgrep -af mpv',shell=True)
        if player:
            return player.decode('utf8').split(' ')[0]

    @classmethod
    def stop_mpv(cls):
        try: # for Linux device, Mac,Ubuntu,Debain...etc
            return subprocess.check_call('pkill -9 mpv',shell=True)
        except subprocess.CalledProcessError:
            pass

        try:
            pid = cls._pid_of_mpv()
            if not pid: # then mpv player was never invoked,we return here
                return 

            return os.kill(int(pid),9) #kill mpv using os
        except ProcessLookupError:
            pass

        try: # For windows
            return subprocess.check_call('taskkill /f /im mpv.exe',
                            shell=True,stderr=subprocess.PIPE)
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


    @classmethod
    def kill_on_quit(cls):
        cls.stop_mpv()



class MetaData(MP3):
    def __init__(self,track):
        super().__init__(track)


    @property
    def trackDuration(self):
        return self.info.length

