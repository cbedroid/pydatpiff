import sys 
import re
import subprocess
import platform 
import logging 


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
    logit = logging.getLogger()
    logging.basicConfig(level=logging.INFO,format = '%(message)s')

    handler = logging.FileHandler('logs.log')
    handler.setLevel(logging.WARNING)
    _format = logging.Formatter(fixdate(),datefmt="%m/%d/%Y %I:%M:%S %p %Z")
    handler.setFormatter(_format)
    logit.addHandler(handler)

    @classmethod
    def _parseLog(cls,*msg,level='info'):

        msg = ' '.join(msg)
        if level == 'info':
            cls.logit.info(msg)
        elif level == 'warning':
            cls.logit.warning(msg)
        elif level == 'critical':
            cls.logit.critical(msg)


    @classmethod
    def display(cls,*msg):
        cls._parseLog(*msg,level='info')

    @classmethod
    def warn(cls,*msg):
        cls._parseLog(*msg,level='warning')
    
    @classmethod
    def failed(cls,*msg):
        cls._parseLog(*msg,level='critical')
 
class MediaError(Exception):
    """ handle all the Media errors"""
    ERRORS = {
                1: 'No Mixtape was pass to Media',
                2: 'Media not set'
            }

    def __init__(self, error,critical=False):
        if error and error in self.ERRORS:
            e_msg = '\n*--> '+self.ERRORS[error]+' <--*\n'
        elif isinstance(error, str):
            e_msg = '\n%s\n' % error
            print(type(e_msg))
        else:
            error = error
            class_name = re.match(r'.*\.(\w*)', str(self.__class__)).group(1)
            e_msg = '\n*--> %s occured <--*\n' % class_name

        if not critical:
            Logger.warn(e_msg)
        else:
            Logger.failed(e_msg)
            sys.exit(1)



class MixtapesError(MediaError):
    """ handle all the Media errors"""
    ERRORS = {
                1: 'No Mixtapes Found',
                2: 'Invalid category selected',
             }

class AlbumError(MediaError):
    ERRORS = {
                1: 'Mixtapes Not Found',
                2: 'Invalid category selected',
             }

class Mp3Error(AlbumError):
    pass


class RequestError(MediaError):
    # _type = self.__class__._qualname__
    ERRORS = {
               1: 'Invalid url scheme',
               2: 'Request failed',
               3: 'Request Non-200 status code',
              }
