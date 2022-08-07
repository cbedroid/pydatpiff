import re

from mutagen.mp3 import MP3

from pydatpiff.constants import music_symbols, player_state_keys
from pydatpiff.errors import PlayerError
from pydatpiff.frontend.screen import Verbose
from pydatpiff.utils.utils import threader_wrapper


class BaseMeta(type):
    """
    For Authors and Contributors only !
    Metaclass that will force constrains on any subclass that inherit BasePlayer

    The below functions and methodology must be implemented along with subclass.
    They will be forced here in BaseMeta(MetaClass). See: BaseMeta.methods
    """

    # more variables: _songs,current_time

    def __new__(cls, name, bases, attrs):
        methods = [
            "set_track",
            "duration",
            "current_time",
            "_format_time",
            "_seeker",
            "volume",
            "volume_up",
            "volume_down",
            "play",
            "pause",
            "rewind",
            "ffwd",
            "stop",
        ]
        # NOTE: 10/28/2021 - need:  See vlc and mpv player
        #    "_global_volume" - to control initial volume on media switch
        #     "volume_level" - setter and getter
        # more variables: _songs,current_time
        cls._name = name
        cls._bases = bases
        cls._attrs = attrs

        for _ in bases:
            for method in methods:
                if method not in attrs:
                    error = 'Method: "%s.%s" must be implemented in your Derived Class ' "to use BasePlayer" % (
                        name,
                        method,
                    )

                    raise NotImplementedError(error)
        return super().__new__(cls, name, bases, attrs)


class BasePlayer(metaclass=BaseMeta):
    """Media player base controller"""

    _global_volume = 100
    _is_monitoring = False
    _track_start_time = 0

    """
    Set default player state
        E.g.
            "playing": False,
            "paused": False,
            "stopped": False,
            "system_stopped": False,
        }
    """
    # NOTE: do not change `_state` private variables to public variables
    _state = dict((k, False) for k in player_state_keys)

    def __init__(self, *args, **kwargs):
        self._track_loaded = False
        self._track_playing = False
        self._track_paused = False
        self._track_stopped = False
        self._system_stopped = False
        self.auto_manage_state()

    def __len__(self):
        # duration will be forced to be implemented by Meta class
        return int(self.duration)

    def reset_and_update_state(self, update=None):
        """Reset and update  all player's state"""
        self._state.update(playing=False, paused=False, loaded=False, stopped=False)
        #  update state if specified.
        update = update if update else {}
        self._state.update(**update)

    @property
    def name(self):
        if not hasattr(self, "_song"):
            raise PlayerError(2, "Cannot find song's name ")
        return self._song

    @property
    def state(self):
        """Current state of the song being played"""
        if hasattr(self, "_state"):
            return self._state
        else:
            raise PlayerError(3, "def _state")

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def _track_loaded(self):
        """Return player loaded state"""
        return self.state["loaded"]

    @_track_loaded.setter
    def _track_loaded(self, state=False):
        self.state["loaded"] = bool(state)

    @property
    def _track_playing(self):
        """Return the track playing state"""
        # if boolean param not specified, then return the playing state
        return self.state["playing"]

    @_track_playing.setter
    def _track_playing(self, state=False):
        """
        Set the state of playing and pause.

        param: boolean - True or False
                True: sets playing True and pause to False.
                False: sets playing False and pause True.
        """
        self.state["playing"] = state

    @property
    def _track_paused(self):
        return self.state["paused"]

    @_track_paused.setter
    def _track_paused(self, state=False):
        self.state["paused"] = bool(state)

    @property
    def _track_stopped(self):
        return self.state["paused"]

    @_track_stopped.setter
    def _track_stopped(self, state=False):
        self.state["stopped"] = bool(state)

    @property
    def _system_stopped(self):
        return self.state["paused"]

    @_system_stopped.setter
    def _system_stopped(self, state=False):
        self.state["system_stopped"] = bool(state)

    @classmethod
    @threader_wrapper
    def auto_manage_state(cls, *args, **kwargs):
        while True:
            state = dict(
                loaded=False,
                playing=False,
                paused=False,
                stopped=False,
                system_stopped=False,
            )
            if cls._track_loaded and not cls._track_playing:
                if cls.current_time > 0:
                    state.update(dict(loaded=True, paused=True))
                else:
                    state.update(dict(loaded=True))

            elif cls._track_playing:
                state.update(dict(loaded=True, playing=True))

            elif cls._track_paused:
                state.update(dict(loaded=True, paused=True))

            elif cls._track_stopped:
                cls._paused_time = 0
                cls._track_start_time = 0
                state.update(dict(stopped=True))

            elif cls.current_time > cls.duration:
                state.update(dict(stopped=True, system_stopped=True))
                cls.stop

            cls.state = state

    def set_track(self, *args, **kwargs):
        # Media class method needed on all player
        raise NotImplementedError

    @property
    def duration(self, *args, **kwargs):
        raise NotImplementedError

    def _format_time(self, *args, **kwargs):
        """Format current song time to clock format"""
        raise NotImplementedError

    @property
    def info(self):
        """Current state of the song"""
        if not hasattr(self, "_song") or not hasattr(self, "current_time"):
            return "no song loaded"

        if "vlc" in str(self.__class__.__name__).lower():
            # VLC player has its own state manager
            state = re.match(r"[\w.]*\.(\w*)", str(self._player.get_state())).group(1)
        else:
            state = self._state

        symbol = "[]"
        if isinstance(state, str) and state == "NothingSpecial":
            # convert state's str to key/value pairs.
            # On initialization, set all state values => False
            for k, v in self._state.items():
                self._state[k] = False

            vlc_state = state.lower()
            # See vlc.get_state docs for more info on VLC states
            self._state["playing"] = "playing" in vlc_state
            self._state["paused"] = "paused" in vlc_state
            self._state["stopped"] = "ended" in state.lower() or "error" in vlc_state or "stopped" in vlc_state
            self._state["system_stopped"] = "error" in vlc_state

        """
        NOTE: we don't want to reset all state, we only want to update the state and its opposing state
        e.g: playing: True -> paused: False
             paused:True -> playing: False

             stopped: True -> playing: False
             playing: True -> stopped: False
        """

        if self._state.get("paused"):
            self._track_paused = True
            self._track_playing = False
            symbol = music_symbols["paused"]
        elif self._state.get("playing"):
            self._track_playing = True
            self._track_paused = False
            symbol = music_symbols["playing"]
        else:
            self.reset_and_update_state()
            symbol = music_symbols["stopped"]

        # song current time
        current_min, current_sec = self._format_time(self.current_time)
        # song duration
        duration_min, duration_sec = self._format_time(self.duration)

        current_sec = str(current_sec).zfill(2)
        duration_sec = str(duration_sec).zfill(2)
        track_info = "{0}  {1}:{2} - {3}:{4}\n".format(symbol, current_min, current_sec, duration_min, duration_sec)

        is_auto_playing = getattr(self, "_media_autoplay", False)
        autoplay_symbol = music_symbols["autoplay"] if is_auto_playing else ""
        Verbose("\n%s TRACK: %s" % (music_symbols["music"], self.name))
        Verbose(autoplay_symbol, track_info)

    @property
    def volume_level(self):
        """Current media player volume"""
        # TODO implement method to monitor the volume
        return 100

    @volume_level.setter
    def volume_level(self, level):
        """set Current media player volume"""
        self._global_volume = level
        # individual player volume control method here

    def volume_up(self, vol=5):
        """Turn the media volume up"""
        raise NotImplementedError

    def volume_down(self, vol=5):
        """Turn the media volume down"""
        raise NotImplementedError

    def volume(self, vol=None):
        """Set the volume to exact number"""
        raise NotImplementedError

    @property
    def play(self):
        """Play media song"""
        raise NotImplementedError

    @play.setter
    def play(self, *args, **kwargs):
        raise NotImplementedError

    @property
    def pause(self):
        """Pause the media song"""
        raise NotImplementedError

    def _seeker(self, pos=10, rew=True):
        """Rewind and ffwd base controls"""
        raise NotImplementedError

    def rewind(self, pos=10):
        """
        Rewind the media song
             @params: pos:: time(second) to rewind media. default:10(sec)
        """
        raise NotImplementedError

    def ffwd(self, pos=10):
        """
        Fast-forward the media song
            @params: pos:: time(second) to rewind media. default:10(sec)
        """
        raise NotImplementedError

    @property
    def stop(self):
        """Stops the song"""
        raise NotImplementedError


class MetaData(MP3):
    def __init__(self, track):
        super().__init__(track)

    @property
    def track_duration(self):
        return self.info.length
