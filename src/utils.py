import logging 
import platform 
import math
import subprocess

def fixdate():
    date = None
    _f = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    if platform.system() == "Linux":
        try:
            _f = 'date +"%m/%d/%y  %I:%M:%S %p"'
            date = subprocess.check_output(_f).decode('utf-8').strip()
            date += ' %(name)s - %(levelname)s - %(message)s'
        except:
            pass
    else:
        date = _f
    return date



class Logger(object):
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO,format = '%(message)s')

    handler = logging.FileHandler('logs.log')
    handler.setLevel(logging.WARNING)
    _format = logging.Formatter(fixdate(),datefmt="%m/%d/%Y %I:%M:%S %p %Z")
    handler.setFormatter(_format)
    logger.addHandler(handler)

    @classmethod
    def _parseLog(cls,*msg,level='info'):

        msg = ' '.join(msg)
        if level == 'info':
            cls.logger.info(msg)
        elif level == 'warning':
            cls.logger.warning(msg)
        elif level == 'critical':
            cls.logger.critical(msg)


    @classmethod
    def display(cls,*msg):
        cls._parseLog(*msg,level='info')

    @classmethod
    def warn(cls,*msg):
        cls._parseLog(*msg,level='warning')
    
    def failed(cls,*msg):
        cls._parseLog(*msg,level='critical')
    



def converter(file_size):
    """Convert file size and returns user readable size""" 
    if file_size == 0:
        return '0B'
    
    size_name = ['B','KB','MB','GB','TB','PB','EB','ZB','YB']
    change = int(math.floor(math.log(file_size,1024)))
    power = math.pow(1024,change)
    result = round(file_size / power,2)
    return '%s %s'%(result,size_name[change])
 




