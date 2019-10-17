import re
import requests
import logging
from .utils import Logger


class MediaError(Exception):
    """ handle all the Media errors"""
    ERRORS = {
        1: 'No Mixtape was pass to Media',
        2: 'Media not set'
    }

    def __init__(self, error):
        if error and error in self.ERRORS:
            e_msg = '\n*--> '+self.ERRORS[error]+' <--*\n'
        elif isinstance(error, str):
            e_msg = '\n%s\n' % error
            print(type(e_msg))
        else:
            error = error
            class_name = re.match(r'.*\.(\w*)', str(self.__class__)).group(1)
            e_msg = '\n*--> %s occured <--*\n' % class_name

        Logger.warn(e_msg)


class MixtapesError(MediaError):
    """ handle all the Media errors"""
    ERRORS = {
        1: 'No Mixtape was pass to Media',
        2: 'Media not set',
    }


class RequestError(MediaError):
   # _type = self.__class__._qualname__
    ERRORS = {1: 'Invalid url scheme',
              2: 'Request failed',
              3: 'Request Non-200 status code',
              }
