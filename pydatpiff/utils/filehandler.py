import logging
import math
import os
import re
import tempfile

logger = logging.getLogger(__name__)


class Tmp(object):  # pragma: no cover
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
    def remove_temp_file_on_startup():
        """remove all temporary file created by Datpiff on start up"""
        # every tmp file using media player will have this suffix
        suffix = "_datpiff"
        tmp_dir = tempfile.gettempdir()
        for filename in os.listdir(tmp_dir):
            if suffix in filename:
                try:
                    filename = os.path.join(tmp_dir, filename)
                    os.remove(filename)
                except FileNotFoundError:
                    logger.warning("File not found: %s", filename)


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
    def standardize_file_name(name):
        return re.sub(r"[^\w_\s\-.]", "", name)

    @classmethod
    def write_to_file(cls, filename, content, mode="wb"):
        with open(filename, mode) as f:
            f.write(content)

    @staticmethod
    def get_human_readable_file_size(buf_size):
        """Convert file size and returns user readable size"""
        if buf_size == 0:
            return "0B"

        ext = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
        change = int(math.floor(math.log(buf_size, 1024)))
        power = math.pow(1024, change)
        calc = buf_size / power
        file_size = round(calc, 2) if buf_size > 999 else int(calc)
        return "%s%s" % (file_size, ext[change])
