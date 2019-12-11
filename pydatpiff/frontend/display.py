"""
   Custom printing function using logger. 

   Stdout can be disable on startup by setting frontend verbose flag False.
   example:: frontend.verbose = True
"""
import os
import sys 
import logging
from .. import output      

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


def handlespace(w): # for correcting joined args
    return w if any(w.endswith(x) for x in ['\n','\t','\r',' ']) else w +' '


def Print(*args):
    if args:
        output = "  ".join(args)
        if shell: # check for shell:: Python IDLE will return None
            rootLogger.info(output)
        else:
            args = list(args)
            args.extend(['\n'])
            for out in args:
                dummy_call = str(color_text.write(handlespace(out),'stdout'))
                

def Verbose(*args):
    verbose = output()
    if not verbose:
        return 
    Print(*args)


