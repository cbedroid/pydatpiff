"""
Handle all temporary files created by Media player.

It removes the hanging temparary files that are not destroyed.
Since we are creating temporary files to store mp3 content, we need 
to remove these files manually after being used.
python3 module 'signal' sometimes fail to catch  signal 
on certain platform like Windows IDLE.
We create our own, in case user close windows or program dies before 
being able to remove these files. 
"""
import os
import sys 
import threading
import tempfile
from functools import wraps

class Tmp(object):
    def __init__(self):
        pass
         
    @staticmethod
    def removeTmpOnstart():
        # every tmpfile using media player will have this suffix
        suffix = '_datpiff'
        tmp_dir = tempfile.gettempdir()
        if os.path.isdir(tmp_dir):
            for lf in os.listdir(tmp_dir):
                if suffix in lf:
                    try:
                        lf = '/'.join((tmp_dir,lf))
                        os.remove(lf)
                    except Exception as e:
                        pass


    def threader(f):
        @wraps(f)
        def inner(self,*a,**kw):
            t = threading.Thread(target=f,args=(self,a))
            t.start()
            return t
        return inner
    
    @threader
    def delete_tmp(name):
     print('TEMP NAME:',name)
     while True:
      try:
       tmp.close()
       os.remove(name)
       print('File is deleted')
      except Exception as e:
        pass
      if not os.path.isfile(name):
       print('FILE BYE BYE')
       break
     return

