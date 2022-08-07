import math
import os
import re
import tempfile


def get_human_readable_file_size(buf_size):
    """Convert file size and returns user readable size"""
    if buf_size == 0:
        return "0B"

    size_name = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    change = int(math.floor(math.log(buf_size, 1024)))
    power = math.pow(1024, change)
    result = round(buf_size / power, 2)
    return "%s %s" % (result, size_name[change])


class Tmp(object):
    """
    Handle all temporary files created by the media player.

    It removes the hanging temporary files that are not destroyed.
    Since we are creating temporary files to store mp3 content, we need
    to remove these files manually after being used.
    python3 module 'signal' sometimes fail to catch  signal
    on certain platforms like Windows IDLE.
    We create our own, in case user close window or program dies before
    being able to remove these files.
    """

    @staticmethod
    def create():
        """Create a temporary file with the suffix  `__datpiff`"""
        return tempfile.NamedTemporaryFile(suffix="_datpiff", delete=False)

    @staticmethod
    def removeTmpOnStart():
        """remove all temporary file created by Datpiff on start up"""
        # every tmp file using media player will have this suffix
        suffix = "_datpiff"
        tmp_dir = tempfile.gettempdir()
        if os.path.isdir(tmp_dir):
            for lf in os.listdir(tmp_dir):
                if suffix in lf:
                    try:
                        lf = "/".join((tmp_dir, lf))
                        os.remove(lf)
                    except:  # noqa
                        pass


class File:
    @staticmethod
    def is_dir(path):
        path = path or ""
        return os.path.isdir(path)

    @staticmethod
    def is_file(path):
        return os.path.isfile(path)

    @classmethod
    def join(cls, path="", to=""):
        if not cls.is_dir(path):
            path = os.getcwd()
        return os.path.join(path, to)

    @staticmethod
    def standardize_name(name):
        return re.sub(r"[^\w_\s\-.]", "", name)

    @staticmethod
    def write_to_file(filename, content, mode="wb"):
        with open(filename, mode) as f:
            f.write(content)
            return True
