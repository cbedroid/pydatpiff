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

    def show(self, code):
        return self.__error__.get(code)

    @staticmethod
    def makeErrorName(error_code):
        # split and capitalize each name in error code
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
        1: "Invalid category selected",
        2: "invalid input",
        3: "too few characters",
    }


class MediaError(Error):
    """handle all the Media errors"""

    __error__ = {
        1: "no mixtapes found",
        2: "invalid mixtapes object",
        3: "media album not set",
        4: "invalid track index",
        5: "song selection error",
        6: "unsupported media player",
        7: "media player not found",
        8: "song not found",
        9: "song unavailable",
    }


class AlbumError(Error):
    __error__ = {
        1: "Mixtapes Not Found",
        2: "Invalid category selected",
    }


class Mp3Error(Error):
    __error__ = {
        1: "invalid player response",
        2: "no album found",
    }


class DatpiffError(Error):
    __error__ = {
        1: "Datpiff server down",
        2: "Datpiff desktop version failed",
        3: "Datpiff mobile version failed",
    }


class MvpError(Error):
    __error__ = {
        1: "song path does not exist",
    }


class PlayerError(Error):
    __error__ = {
        1: "Unsupported media object",
        2: "no song found",
        3: "derive class missing function",
        4: "call back method missing",
        5: "unsupported player",
        6: "player not found",
    }


class RequestError(Error):
    # _type = self.__class__._qualname__
    __error__ = {
        1: "datpiff server",
        2: "connection time out",
        3: "invalid url",
        4: "request error",
    }


class BuildError(Error):
    __error__ = {
        1: "user selection",
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
        1: "Pydatpiff installion error",
    }
