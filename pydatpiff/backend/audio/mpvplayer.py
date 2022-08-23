import re
from functools import wraps
from time import sleep, time

from pydatpiff.errors import MvpError
from pydatpiff.frontend.screen import Verbose
from pydatpiff.utils.filehandler import File

from .audio_engine import Popen
from .baseplayer import BasePlayer, MetaData


class MPV(BasePlayer):
    # 10 mins:  Time to kill inattentive threads see pause.
    # Save the user's CPU :-)
    _MAX_INACTIVITY = 60 * 10

    def __init__(self):
        self.time_captured = None
        self._song_path = None
        self._song = None
        self._popen = None
        super().__init__()

        # making Baseplayer state -> private to public
        self.state = self._state

    def _pre_popen(self, song):
        return [
            "mpv",
            "--input-terminal=yes",
            "-no-audio-display",
            "--input-file=/proc/self/fd/0",
            "--no-term-osd",
            "--osc=no",
            "%s" % song,
        ]

    def _pause_handler(self):
        """
        Captures the time duration when the track is paused.
        Once track is unpause time will be added back to the original track time
        This time will be used to calculate the accuracy of current_position
        when pause state changes from pause to playing.
        """
        rollback = 0
        while True:
            rollback += 1
            if not self._track_paused or self._track_playing:
                self._track_start_time += rollback
                return
            sleep(1)  # must use sleep to prevent high cpu usage while threading

            if rollback > self._MAX_INACTIVITY:
                Verbose('Pydatpiff program was killed due to "Pause Inactivity"...')
                exit(1)

    def _run_pause_handler(self):
        import threading

        t = threading.Thread(target=self._pause_handler)
        t.daemon = True
        t.start()

    @property
    def duration(self):
        """Return track length  in seconds"""
        if hasattr(self, "_metadata"):
            return self._metadata.track_duration
        return 0

    def _format_time(self, pos=None):
        """Format current song time to clock format"""
        pos = self.duration if not pos else pos
        minutes = int(pos / 60)
        seconds = int(pos % 60)
        return minutes, seconds

    @property
    def current_time(self):
        """Current time of track"""
        time_now = time() - self._track_start_time
        # always capture time to adjust pause time
        self.time_captured = time_now

        if self._track_stopped:
            return 0

        return time_now

    @current_time.setter
    def current_time(self, timer):
        if not self._track_stopped:
            self._track_start_time += timer

    def _sync_track_time(self, sec):
        """
        Adjust the track's time in seconds when track is
        being rewinding, fast-forwarding, or paused.
        """
        constrains = self._constrain_seek(sec)
        self.time_captured += constrains

    def _constrain_seek(self, seek):
        """Force range constraints on setting seek time,
        when rewinding and fast-forwarding.
        Time that is set out of range will be set to its nearest position.
        """
        seek = float(seek)
        current_pos = self.current_time

        # rewind past track's starting point
        if current_pos + seek < 0:
            return 0
        # ffwd past track's duration, then set track 5 seconds before ending.
        elif len(self) < current_pos + seek:
            # self.track_stopped = True
            return len(self) - 5.0

        return int(seek) * -1

    def _seek_syncer(func):
        """
        Callback function that force track time to be synced with the time
        whenever track position is being seeked see: MPV._seeker.
        """

        @wraps(func)
        def inner(self, time_sec):
            self._sync_track_time(time_sec)
            return func(self, time_sec)

        return inner

    @_seek_syncer
    def _seeker(self, sec=5):
        """
        Control fast-forward and rewind function.

        :param: pos - time to rewind or fast-forward (in seconds)
        """

        raw_sec = re.sub(r"-", "", str(sec))
        if not raw_sec.isnumeric():
            Verbose("Must use numerical numbers")
            return
        seek = "seek %s \n" % sec
        self._write_cmd(seek)
        return int(sec)

    def set_track(self, name, path):
        # media class method

        if File.is_file(path):
            self._song = name
            self._song_path = path
            self._metadata = MetaData(path)
            self._track_loaded = True
            self._track_start_time = time()
            self._volume = self._global_volume
            self.auto_manage_state()
        else:
            raise MvpError(1)

        Popen.unregister()

    def _write_cmd(self, cmd):
        """
        Write command to Popen stdin
        param: cmd - string character to write
        """

        if getattr(self, "_popen"):
            if self._track_loaded and self._popen.is_alive:
                self._popen.stdin.write("{}\n".format(cmd).encode("utf8"))
                self._popen.stdin.flush()
                return

    @property
    def play(self):
        # set_track method will handle the loadeding of track
        if self._track_loaded:
            if self._track_playing:
                return
            # if track not loaded, then load it and play
            self._popen = Popen(self._pre_popen(self._song_path))
            self._popen.register()
            self._track_loaded = True
            self._track_playing = True
            self.play  # noqa  - this is a property function in baseplayer
            self._volume = self._global_volume

    @property
    def pause(self):
        """Pause and unpause the track."""

        if self._track_loaded:
            if self._track_playing:
                cmd = "set pause yes \n"
                self._write_cmd(cmd)
                self._track_playing = False
                self._track_paused = True
                self._run_pause_handler()
            else:
                Verbose("\nUnpause")
                self._track_paused = False
                self._track_playing = True
                cmd = "set pause no \n"
                self._write_cmd(cmd)
        else:
            Verbose("No track playing")

    def rewind(self, sec=5):
        """
        Rewind track.

        :param: pos - time to rewind or fast-forward (in seconds)
        """

        sec = "-" + str(sec)
        self._seeker(sec)

    def ffwd(self, sec=5):
        """
        Fast-forward track.
            :param: pos - time to rewind or fast-forward (in seconds)
        """
        sec = str(sec)
        self._seeker(sec)

    @property
    def stop(self):
        """Stop the current track from playing."""
        self._write_cmd("quit \n")
        self._track_stopped = True
        Popen.unregister()

    @property
    def _volume(self):
        """Current media player volume"""
        return self._global_volume

    @_volume.setter
    def _volume(self, level):
        self._global_volume = level

    def volume(self, level=None):
        """Set the volume to exact number"""
        MAX_LEVEL = 200
        if not level or not isinstance(level, int):
            return

        if level > MAX_LEVEL:
            level = MAX_LEVEL

        elif level < 0:
            level = 0

        self._volume = level
        self._write_cmd("set volume %s" % level)

    def volume_up(self, vol=5):
        """Turn the media volume up"""

        if not isinstance(vol, int):
            return

        self._volume += vol

    def volume_down(self, vol=5):
        """Turn the media volume down"""

        if not isinstance(vol, int):
            return

        self._volume -= vol
