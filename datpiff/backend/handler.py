import os
import sys 
import re
import threading
import tempfile
import platform 
import math
import subprocess
from functools import wraps


def converter(file_size):
    """Convert file size and returns user readable size""" 
    if file_size == 0:
        return '0B'
    
    size_name = ['B','KB','MB','GB','TB','PB','EB','ZB','YB']
    change = int(math.floor(math.log(file_size,1024)))
    power = math.pow(1024,change)
    result = round(file_size / power,2)
    return '%s %s'%(result,size_name[change])
 

class Tmp(object):
    """
    Handle all temporary files created by Media player.

    It removes the hanging temparary files that are not destroyed.
    Since we are creating temporary files to store mp3 content, we need 
    to remove these files manually after being used.
    python3 module 'signal' sometimes fail to catch  signal 
    on certain platform like Windows IDLE.
    We create our own, in case user close window or program dies before 
    being able to remove these files. 
    """

    def __init__(self):
        pass

    @staticmethod
    def create():
        """Create a temporary file with suffix __datpiff"""
        return tempfile.NamedTemporaryFile(suffix='_datpiff',delete=False)
         

    @staticmethod
    def removeTmpOnstart():
        """remove all temporary file created by Datpiff on start up"""
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


class Path():
    @staticmethod
    def is_dir(path):
        path = path or ''
        return os.path.isdir(path)

    @classmethod
    def join(cls,path='',to=''):
        if not cls.is_dir(path):
            path = os.getcwd()
        return os.path.join(path,to)

    @staticmethod
    def toStandard(name):
        return re.sub('[^A-Za-z1-9_\-\.] ', '', name)

