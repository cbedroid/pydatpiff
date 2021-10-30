import re

import vlc

from pydatpiff.errors import PlayerError
from pydatpiff.frontend.screen import Verbose

from .baseplayer import BasePlayer


class VLCPlayer(BasePlayer):
    def __init__(self, *args, **kwargs):
        try:
            self._vlc = vlc.Instance("-q")
            self._player = self._vlc.media_player_new()
        except:
            extended_msg = "Please check if your device supports VLC"
            raise PlayerError(1, extended_msg)

        self._volume = self._global_volume
        super().__init__(*args, **kwargs)

    @property
    def duration(self):
        return self._player.get_length()

    def _format_time(self, pos=None):
        """Format current song time to clock format"""
        mins = int(pos / 60000)
        secs = int((pos % 60000) / 1000)
        return mins, secs

    @property
    def current_time(self):
        return self._player.get_time()

    @property
    def info(self):
        """Current state of the song being played"""
        state = re.match(r"[\w.]*\.(\w*)", str(self._player.get_state())).group(1)
        if state == "NothingSpecial":
            # set all player value to False
            for k, v in self._state.items():
                self._state[k] = False
        elif "pause" in state.lower():
            self._track_paused = True
            self._track_playing = False
        else:
            self._track_playing = True
            self._track_paused = False
        return self.state

    def setTrack(self, name, path=None):
        if path:
            self._song = name
            self._path = path
            self._player.set_mrl(path)
            self._track_loaded = True
            self._volume = self._global_volume
        else:
            Verbose("No media to play")

    @property
    def _volume(self):
        """Get current media player volume"""
        return self._player.audio_get_volume()

    @_volume.setter
    def _volume(self, level):
        """Set media player volume"""
        if level < 0:
            level = 0
        if level > 100:
            level = 100

        self._player.audio_set_volume(level)
        self._global_volume = level

    def volumeUp(self, level=5):
        """Turn the media volume up"""
        if not level and not isinstance(level, int):
            return
        self._volume += level

    def volumeDown(self, level=5):
        """Turn the media volume down"""
        if not level and not isinstance(level, int):
            return
        self._volume -= level

    def volume(self, level):
        """Set the volume to exact number"""
        if not level or not isinstance(level, int):
            return
        self._volume = level

    @property
    def play(self):
        """Play media song"""
        if not self._track_stop:
            if self._track_paused:
                # unpause if track is already playing but paused
                self.pause
            else:
                self._player.play()

            self._track_playing = True
            return
        else:
            try:
                self.setTrack(self._song, self._path)
                self.state["stop"] = False
                return self.play
            except RecursionError:
                self.state["stop"] = True

    @property
    def pause(self):
        """Pause the media song"""

        pause = self._track_paused
        self._track_playing = pause
        self._player.pause()
        self._track_paused = not pause

    def _seeker(self, pos=10, rew=True):
        if self._state["stop"]:
            return
        if rew:
            to_position = self._player.get_time() - (pos * 1000)
            # seeking far before track starts
            if to_position < 0:
                to_position = 0
        else:
            to_position = self._player.get_time() + (pos * 1000)
            # seeking too far beyond track ends
            if to_position > self.duration:
                to_position = self.duration - 1

        self._player.set_time(to_position)

    def rewind(self, pos=10):
        """Rewind track
        @params: pos:: time(second) to rewind media. default:10(sec)
        """
        self._seeker(pos, True)

    def ffwd(self, pos=10):
        """Fast forward track
        vlc time is in milliseconds
        @params: pos:: time(second) to rewind media. default:10(sec)
        """
        self._seeker(pos, False)

    @property
    def stop(self):
        self._player.stop()
        self._track_stop = True
