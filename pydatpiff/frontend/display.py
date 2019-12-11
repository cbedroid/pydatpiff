"""
   Custom printing function using logger. 

   Stdout can be disable on startup by setting frontend verbose flag False.
   example:: frontend.verbose = True
"""
import os
import sys 
import logging
import pydatpiff

rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)
shell = os.environ.get('SHELL')
# use stdout if shell is None
try:
    color_text = sys.stdout.shell
except:
    class color_text():
        @classmethod
        def write(*text):
            text = text[0]
            print(text)


def Print(*args):
    if args:
        args = "  ".join(args)
        if shell: # check for shell:: Python IDLE will return None
            rootLogger.info(args)
        else:
            dummy_call = str(color_text.write(args,'stdout'))

def Verbose(*args):
    if not pydatpiff.pydatpiff.verbose:
        return 
    Print(*args)


