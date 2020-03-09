import subprocess 
from mutagen.mp3 import MP3
from ..config import Threader




class Popen(subprocess.Popen):
    def __init__(self,*args,**kwargs):
        """ build subprocess Popen object"""

        self.kill_on_start()
        kwargs['stdin']  = subprocess.PIPE
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE
        super().__init__(*args,**kwargs)    

    @staticmethod
    def kill_on_start():
        try:
            subprocess.check_output('pkill -9 mpv',shell=True)
        except:
            try:
                subprocess.check_output('sudo pkill -9 mpv',shell=True)
            except:
                pass


    @Threader
    def register(self,callback,*args,**kwargs):
        """
        Kills subprocess Popen when error occur or when 
        process job finish"""
        print('Registering POLL')

        while True:
            if self.poll() is not None:
                print('Killing Popen')
                callback(*args,**kwargs)
                self.kill()
                break
                

class MetaData(MP3):
    def __init__(self,track):
        super().__init__(track)


    @property
    def trackDuration(self):
        return self.info.length



           



