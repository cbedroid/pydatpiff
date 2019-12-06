"""
   Custom printing function using logger. 

   Stdout can be disable on startup by setting frontend verbose flag False.
   example:: frontend.verbose = True
"""
import logging
import pydatpiff 

rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

def Print(*args):
    if args:
        args = "  ".join(args)
        rootLogger.info(args)

def Verbose(*args):
    if not pydatpiff.pydatpiff.verbose:
        return 
    Print(*args)


