import os 
import sys 
import re
import subprocess
import platform 
import tempfile 
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
    logit = logging.getLogger(__name__)
    logging.basicConfig(level=logging.WARNING,format = '%(message)s')
    logfile = os.path.join(tempfile.gettempdir(),'pydatpiff.log')
    handler = logging.FileHandler(logfile)
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
 


class Error(Exception):
    __error__ = {
                 1:'invalid mixtapes object',
                 2:'no mixtapes found'
                }

    code = None
    message='Unknown'


    def __init__(self,code,detail=''):
        self._code = code
        code = self.create(code,detail)
        super().__init__(code)


    def logError(self, error,critical=False):
        if error and error in self.__error__:
            if not critical:
                Logger.warn(self.__error__[error])
            else:
                Logger.failed(self.__error__[error])
                sys.exit(1)


    def show(self,code):
        return self.__error__.get(code)



    @staticmethod
    def makeError(code):
        #code = code or self.message
        cont = []
        for x  in code.split(' '):
            cont.append(x.capitalize())
        cont = ''.join(cont)
        return cont


    @classmethod
    def create(cls,export_to,long_msg=''):
        if isinstance(export_to,str):
            max_e = max(cls.__error__)
            cls.__error__[max_e+1] = Error.makeError(export_to)
            return Error.create(max_e+1)
        elif export_to in cls.__error__:
            for code,error in cls.__error__.items():
                if not isinstance(error,str):
                    return error
                name = Error.makeError(error)
                e = type(name,(cls,),{
                    'code': code,
                    'message':error,
                    })
                cls.__error__[code] = e  
            return "".join((str(cls.__error__[export_to]),'\n'+long_msg))
   


class MixtapesError(Error):
    """ handle all the Mixtapes errors"""
    __error__ = {
                 1: 'No Mixtapes Found',
                 2: 'Invalid category selected',
                 3: 'Unable to process Data',
                }


class MediaError(Error):
    """ handle all the Media errors"""
    __error__ = {
                 1: 'no mixtapes found',
                 2: 'invalid mixtapes object',
                 3: 'media album not set',
                 4: 'invaild track index',
                 5: 'song selection error',
                 6: 'unsupported media player',
                 7: 'media player not found',
                 8: 'song cache storage failed',
                }


class AlbumError(Error):
    __error__ = {
                  1: 'Mixtapes Not Found',
                  2: 'Invalid category selected',
                }


class Mp3Error(Error):
    __error__  = {
                   1: 'player id error',
                 }
 

class MvpError(Error):
    __error__  = {
                   1: 'song path does not exist',
                 }
 
class PlayerError(Error):
    __error__  = {
                   1: 'Unsupport media object',
                   2: 'no song found',
                   3: 'derive class missing function',
                   4: 'call back method missing'
                 }    


class RequestError(Error):
    # _type = self.__class__._qualname__
    __error__ = {
                 1: 'invalid url scheme',
                 2: 'web page timed out',
                 3: 'request failed',
                 4: 'requests status code error',
                }


class BuildError(Error):
    __error__ = {
                 1, 'user selection',
                }

class InstallationError(Error):
    _extra = "\nPydatpiff Audio requires either VLC or MPV installation." \
            "\n\nView"\
            " https://github.com/cbedroid/pydatpiff/blob/master/README.md" \
            " for more installation instructions."""
    __error__ = {
                 1, 'Pydatpiff installion error',
                }

