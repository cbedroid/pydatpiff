__author__ = 'Cornelius Brooks'
__date__ = 'Feb 3, 2019'
__description__ =''' Datpiff music player that lets user control,download, and play  music from cmdline  '''
__version__ = 'V1.0.1'

from .media import Media 
from .mixtapes import Mixtapes
from .logger import Logger
from .utils.request import Session
from .utils.helper import String
from .utils.handler import *

