import logging
import os
import platform
import subprocess
import sys
import tempfile


def fixdate():
    date = None
    _f = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if platform.system() == "Linux":
        try:
            _f = 'date +"%m/%d/%y  %I:%M:%S %p"'
            date = subprocess.check_output(_f).decode("utf-8").strip()
            date += " %(name)s - %(levelname)s - %(message)s"
        except:
            pass
    else:
        date = _f
    return date


class Logger(object):
    logit = logging.getLogger(__name__)
    logging.basicConfig(level=logging.WARNING, format="%(message)s")
    logfile = os.path.join(tempfile.gettempdir(), "pydatpiff.log")
    handler = logging.FileHandler(logfile)
    handler.setLevel(logging.WARNING)
    _format = logging.Formatter(fixdate(), datefmt="%m/%d/%Y %I:%M:%S %p %Z")
    handler.setFormatter(_format)
    logit.addHandler(handler)

    @classmethod
    def _parseLog(cls, *msg, level="info"):

        msg = " ".join(msg)
        if level == "info":
            cls.logit.info(msg)
        elif level == "warning":
            cls.logit.warning(msg)
        elif level == "critical":
            cls.logit.critical(msg)

    @classmethod
    def display(cls, *msg):
        cls._parseLog(*msg, level="info")

    @classmethod
    def warn(cls, *msg):
        cls._parseLog(*msg, level="warning")

    @classmethod
    def failed(cls, *msg):
        cls._parseLog(*msg, level="critical")


class Error(Exception):
    __error__ = {
        1: "invalid mixtapes object",
        2: "no mixtapes found",
    }

    code = None
    message = "Unknown"

    def __init__(self, code, detail=""):
        self._code = code
        code = self.create(code, detail)
        super().__init__(code)

    def logError(self, error, critical=False):
        if error and error in self.__error__:
            if not critical:
                Logger.warn(self.__error__[error])
            else:
                Logger.failed(self.__error__[error])
                sys.exit(1)

    def show(self, code):
        return self.__error__.get(code)

    @staticmethod
    def makeErrorName(error_code):
        # split and titlize each name in error code
        error_name = "".join(list(map(lambda x: x.title(), error_code.split(" "))))

        if not (error_name.lower()).endswith("error"):
            error_name += "Error"
        return error_name

    @classmethod
    def create(cls, error_code, extra_message=""):
        if isinstance(error_code, str):
            max_errors = max(cls.__error__)
            cls.__error__[max_errors + 1] = Error.makeErrorName(error_code)
            return Error.create(max_errors + 1)

        elif error_code in cls.__error__:
            for code, error in cls.__error__.items():
                if not isinstance(error, str):
                    return error

                error_class_name = Error.makeErrorName(error)
                error_class = type(
                    error_class_name,
                    (cls,),
                    {"code": code, "message": error},
                )
                # apply the new error to the base error class
                # basically we are caching the new error
                cls.__error__[code] = error_class

            error_name = cls.__error__[error_code].__name__
            return "\n".join((error_name, extra_message))


class MixtapesError(Error):
    """handle all the Mixtapes errors"""

    __error__ = {
        1: "No Mixtapes Found",
        2: "Invalid category selected",
        3: "Unable to process Data",
        4: "Invalid data type",
        5: "TooFewCharacters",
    }


class MediaError(Error):
    """handle all the Media errors"""

    __error__ = {
        1: "no mixtapes found",
        2: "invalid mixtapes object",
        3: "media album not set",
        4: "invaild track index",
        5: "song selection error",
        6: "unsupported media player",
        7: "media player not found",
        8: "song cache storage failed",
    }


class AlbumError(Error):
    __error__ = {
        1: "Mixtapes Not Found",
        2: "Invalid category selected",
    }


class Mp3Error(Error):
    __error__ = {
        1: "player id error",
    }


class DatpiffError(Error):
    __error__ = {
        1: "Datpiff media server down",
        2: "Datpiff desktop version failed",
        3: "Datpiff mobile version failed",
    }


class MvpError(Error):
    __error__ = {
        1: "song path does not exist",
    }


class PlayerError(Error):
    __error__ = {
        1: "Unsupport media object",
        2: "no song found",
        3: "derive class missing function",
        4: "call back method missing",
        5: "unsupported player",
    }


class RequestError(Error):
    # _type = self.__class__._qualname__
    __error__ = {
        1: "invalid url scheme",
        2: "web page timed out",
        3: "request failed",
        4: "requests status code error",
    }


class BuildError(Error):
    __error__ = {
        1,
        "user selection",
    }


class InstallationError(Error):
    _extra = (
        "\nPydatpiff Audio requires either VLC or MPV installation."
        "\n\nView"
        " https://github.com/cbedroid/pydatpiff/blob/master/README.md"
        " for more installation instructions."
        ""
    )
    __error__ = {
        1,
        "Pydatpiff installion error",
    }
