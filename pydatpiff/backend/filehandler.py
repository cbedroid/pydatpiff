import os
import re
import tempfile
import math

class Dict():
    def __init__(self):
        self.data = collection.defaultdict(dict)

    def setAttr(self,name,_list,start=1):
        """Convert list object to a enumerate dictionary"""
        for count,data in enumerate(_list,start=start):
            self.data[count][name] = data
        


def file_size(buf_size):
    """Convert file size and returns user readable size""" 
    if buf_size == 0:
        return '0B'
    
    size_name = ['B','KB','MB','GB','TB','PB','EB','ZB','YB']
    change = int(math.floor(math.log(buf_size,1024)))
    power = math.pow(1024,change)
    result = round(buf_size / power,2)
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

class Path():
    @staticmethod
    def is_dir(path):
        path = path or ''
        return os.path.isdir(path)

    @staticmethod
    def isFile(path):
        """ 
        Check if file path exists 
        :params: path - path of song 
        """
        return os.path.isfile(path)


    @classmethod
    def join(cls,path='',to=''):
        if not cls.is_dir(path):
            path = os.getcwd()
        return os.path.join(path,to)

    @staticmethod
    def standardizeName(name):
        return re.sub('[^A-Za-z0-9_\-\.] ', '', name)

    @staticmethod
    def writeFile(filename,content,mode='wb'):
        with open(filename,mode) as f:
            f.write(content)
            return True

            
