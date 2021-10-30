"""
   Custom printing function using logger.
"""
from pydatpiff.utils.logging import logging

logger = logging.getLogger(__name__)


def Verbose(*args):
    output = " ".join(args)
    logger.info(output)


def display_play_message(artist, album_name, song_name, size, demo=False):
    if demo:
        Verbose("\n%s %s %s" % ("-" * 20, "DEMO", "-" * 20))
    Verbose("\nAlbum: %s" % album_name)
    Verbose("Artist: %s" % artist)
    Verbose("Song: %s" % song_name)
    Verbose("Size:", size)


def display_download_message(song_name, size):
    Verbose("\nDownloading:", song_name, "\nSIZE:  ", size)
