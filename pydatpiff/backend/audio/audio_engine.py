import atexit
import logging
import os
import platform
import subprocess

from pydatpiff.errors import PlayerError
from pydatpiff.utils.utils import threader_wrapper

logger = logging.getLogger(__name__)


class Popen(subprocess.Popen):  # pragma: no cover
    registered_popen = []
    _player_PID = None

    def __init__(self, *args, **kwargs):
        """build subprocess Popen object"""
        kwargs["stdin"] = subprocess.PIPE
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.PIPE
        atexit.register(self.kill_on_quit)
        try:
            super().__init__(shell=False, *args, **kwargs)
            self._player_PID = self.pid
        except:
            logger.exception("PlayerPopenFailed")
            # throws PlayerNotFoundError
            raise PlayerError(6)

    def stop_player(self):
        if platform.system() == "Windows":
            # https://tweaks.com/windows/39559/kill-processes-from-command-prompt/
            kill_cmd = ("taskkill /pid {} /F",)
        else:
            # Systems: Linux, Darwin ..etc
            kill_cmd = "kill -9 {}"

        try:  # For Linux device, Mac, Ubuntu, Debain...etc
            if self._player_PID:
                return subprocess.check_call(
                    kill_cmd.format(self._player_PID),
                    shell=True,
                    stderr=subprocess.PIPE,
                )
        except subprocess.CalledProcessError:
            return os.kill(int(self._player_PID), 9)  # kill mpv using os
        except:
            logger.exception("Failed to kill player")

    @threader_wrapper
    def register(self, callback=None, *args, **kwargs):
        """
        Kills subprocess Popen when error occur or when process job finish

        Args:
            callback (function, optional): Function to execute once player process dies.
        """
        self.registered_popen.append(self)

        # constantly probe Popen to check if player is running
        while True:
            if self.poll() is not None:
                if callback:
                    callback(*args, **kwargs)
                self.kill()
                break

    @classmethod
    def unregister(cls):
        """Unregister and terminate Popen process"""
        for popen in cls.registered_popen:
            popen.kill()

    @property
    def is_alive(self):
        if self.poll() is None:
            return True
        return False

    def kill_on_quit(self):
        if self.is_alive:
            self.stop_player()

    def kill_on_start(self):
        for process in self.registered_popen:
            process.kill()
