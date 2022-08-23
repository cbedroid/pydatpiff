import os
import re
from tempfile import TemporaryDirectory as TempDir
from unittest.mock import Mock, PropertyMock, patch

from pydatpiff import media, mixtapes
from pydatpiff.backend import mediasetup
from pydatpiff.constants import verbose_message
from pydatpiff.errors import MediaError, PlayerError
from pydatpiff.utils.filehandler import File
from tests.utils import BaseTest


class VLCPlayer:
    pass


class MPV:
    pass


class BaseMediaTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # mocked mixtapes
        mix_content = cls.get_request_content("mixtape")
        mixtapes.Session.method = Mock(autospec=True, return_value=cls.mocked_response(content=mix_content))
        cls.mix = mixtapes.Mixtape()

        # mocked media
        cls.media_request_content = cls.get_request_content("media")
        cls.method = media.Session.method = Mock(autospec=True)
        cls.method.return_value = cls.mocked_response(content=cls.media_request_content)

        # mock mediasetup Album's embed player response
        mocked_embed_player_response = cls.get_request_content("embed_player")
        mediasetup_session = mediasetup.Session.method = Mock(autospec=True)
        mediasetup_session.return_value = cls.mocked_response(content=mocked_embed_player_response)

        # Un-mocked media
        cls.unmocked_media = media.Media(cls.mix)
        cls.unmocked_media.setMedia(1)

        cls.media = media.Media(cls.mix)

        # Mocked retrieving song name and song content
        cls.mock_get_audio = cls.media._get_audio_track = Mock(
            return_value=(cls.song_list[0], cls.get_song_content()), autospec=True
        )
        # Mocked file descriptor for writing song content (io buffer)
        cls.mocked_write_audio = cls.media._write_audio = Mock(return_value=cls.get_song_content())
        cls.media._song_index = 0
        cls.media.setMedia(1)

        # Add test artist and album (mixtape)
        cls.test_artist = cls.artist_list[0]
        cls.test_album = cls.mixtape_list[0]

    def tearDown(self):
        # Prevent pytest from hanging due sto `while loop` in player
        self.media.player.stop
        self.unmocked_media.player.stop


class TestMedia(BaseMediaTest):
    def test_media_raises_an_exception_when_mixtape_is_not_a_valid_mixtape_type(self):
        with self.assertRaises(MediaError):
            media.Media(object)

        with self.assertRaises(MediaError) as context:
            media.Media()
            self.assertEqual(context.exception.code, 1)

    @patch.object(media.Player, "getPlayer")
    def test_media_player_parameter_has_a_valid_media_player_application(self, mocked_get_player):
        mocked_get_player.return_value = VLCPlayer()
        my_media = media.Media(self.mix, player="vlc")
        self.assertEqual(mocked_get_player.call_count, 1)
        self.assertEqual(my_media.player.__class__, VLCPlayer)

        mocked_get_player.return_value = MPV()
        my_media = media.Media(self.mix, player="mpv")
        self.assertEqual(mocked_get_player.call_count, 2)
        self.assertEqual(my_media.player.__class__, MPV)

    def test_invalid_audio_player_program_raises_player_error(self):
        with self.assertRaises(PlayerError) as context:
            media.Media(self.mix, player="invalid")
            self.assertEqual(context.exception.code, 5)

    def test_media_default_media_player_is_set_to_MPV_player(self):
        from pydatpiff.backend.audio.player import MPV as MPVPlayer

        media_player = media.Media(self.mix)
        self.assertEqual(media_player.player.__class__, MPVPlayer)

    def test_media_len_method_return_correct_length(self):
        self.assertEqual(len(self.media), len(self.song_list))

    def test_media_len_method_when_media_is_not_set_to_an_album(self):
        media_player = media.Media(self.mix)
        self.assertEqual(len(media_player), 0)

    def test_media_album_can_be_selected_by_index(self):
        indexed_media = media.Media(self.mix)
        indexed_media.setMedia(0)
        self.assertEqual(self.test_album, indexed_media.album.name)

        named_media = media.Media(self.mix)
        named_media.setMedia(self.test_album)
        self.assertEqual(self.test_album, named_media.album.name)

        self.assertEqual(indexed_media.album.name, named_media.album.name)

    @patch.object(media.Album, "name", new_callable=PropertyMock)
    def test_selecting_a_mixtapes_out_of_range_correctly_set_media_to_last_mixtapes(self, mocked_album_name):
        # User set a mixtapes that is larger than the total number of the mixtapes
        mocked_album_name.return_value = self.mix.mixtapes[-1]
        media_player = media.Media(self.mix)
        media_player.setMedia(2000)
        self.assertEqual(media_player.album.name, self.mix.mixtapes[-1])

    def test_media_raises_MediaError_when_passed_an_invalid_mixtapes_object(self):
        with self.assertRaises(MediaError) as context:
            media.Media(object)
            self.assertEqual(context.exception.code, 1)

    @patch.object(media.ThreadQueue, "execute", autospec=True)
    def test_media_find_song_method_returns_correct_albums(self, queue):
        query_result = {
            "index": 1,
            "album": self.mixtape_list[0],
            "song": self.song_list[0],
        }
        queue.return_value = [query_result]
        response = self.media.find_song("Switches")
        self.assertIn(query_result, response)

    @patch.object(media.ThreadQueue, "execute", autospec=True)
    @patch.object(media, "Verbose", autospec=True)
    def test_verbose_message_is_displayed_when_song_is_not_found(self, mocked_verbose, mocked_queue):
        mocked_queue.return_value = []
        song_name = "unknown song"
        self.media.find_song(song_name)
        mocked_verbose.assert_called_with(verbose_message["SONG_NOT_FOUND"] % song_name)

    def test_media_sets_album_name_is_correct(self):
        album = self.test_album
        self.assertEqual(album, self.media.album.name)

    def test_media_sets_artist_name_correctly(self):
        self.assertEqual(self.test_artist, self.media.artist)

    def test_media_sets_album_cover_url_correctly(self):
        album_cover = self.media.album_cover
        self.assertIsNotNone(album_cover)
        # test album name is in  album cover url
        filter_character = re.sub(r"[^\w\s]", "", self.test_album)
        url_encoded_name = re.sub(r"\s", "_", filter_character)
        self.assertIn(url_encoded_name, album_cover)

    def test_media_set_correct_mixtapes_songs(self):

        # test song is in media album
        songs = self.media.songs
        self.assertIn(self.song_list[0], songs)
        # test songs total is correct
        self.assertCountEqual(self.song_list, songs)

    @patch.object(media, "Verbose", autospec=True)
    def test_media_set_song_when_song_is_being_played(self, mocked_verbose):
        media_player = media.Media(self.mix)
        media_player.setMedia(self.test_album)

        media_player.song = self.song_list[0]
        self.assertEqual(media_player.song, self.song_list[0])

        # test error message when song is not found
        media_player.song = "some-unknown-song"
        mocked_verbose.assert_called_with(verbose_message["SONG_NOT_FOUND"] % "some-unknown-song")

    @patch.object(media, "Verbose", autospec=True)
    def test_show_songs_method_print_all_songs(self, mocked_verbose):
        self.media.show_songs()
        self.assertEqual(mocked_verbose.call_count, len(self.song_list))

        # test verbose message when media is not set to an album
        media_player = media.Media(self.mix)
        media_player.show_songs()
        mocked_verbose.assert_called_with(verbose_message["MEDIA_NOT_SET"])

    @patch.object(media.Media, "song", new_callable=PropertyMock)
    def test_media_plays_song_by_index_correctly(self, mocked_song):
        # test play song by referencing song index
        mocked_song.return_value = self.song_list[0]
        self.media.play(1, demo=True)
        self.assertEqual(self.media.song, self.song_list[0])

    @patch.object(media.Media, "song", new_callable=PropertyMock)
    def test_playing_song_that_is_out_of_range_plays_last_song(self, mocked_song):
        # test play song by referencing song index
        mocked_song.return_value = self.song_list[-1]
        self.media.play(100000)
        self.assertEqual(self.media.song, self.song_list[-1])

    @patch.object(media.Media, "song", new_callable=PropertyMock)
    @patch.object(media, "Verbose", autospec=True)
    def test_song_can_be_played_by_referencing_song_name(self, mocked_verbose, mocked_song):
        # test play song by referencing full song mame
        mocked_song.return_value = self.song_list[0]
        self.media.play(self.song_list[0])
        self.assertEqual(self.media.song, self.song_list[0])
        mocked_verbose.assert_not_called()

    @patch.object(media.Media, "song", new_callable=PropertyMock)
    @patch.object(media, "Verbose", autospec=True)
    def test_song_can_be_played_by_referencing_partial_song_name(self, mocked_verbose, mocked_song):
        # test play song by referencing partial song mame
        mocked_song.return_value = self.song_list[0]
        self.media.play(self.song_list[0][:3])
        self.assertEqual(self.media.song, self.song_list[0])
        mocked_verbose.assert_not_called()

    @patch.object(media.Media, "song", new_callable=PropertyMock)
    @patch.object(media, "Verbose", autospec=True)
    def test_play_song_by_name_is_case_insensitive(self, mocked_verbose, mocked_song):
        # test play song is case-insensitive
        mocked_song.return_value = self.song_list[0]
        self.media.play(self.song_list[0][:3].upper())
        self.assertEqual(self.media.song, self.song_list[0])
        mocked_verbose.assert_not_called()

    @patch.object(media.Media, "song", new_callable=PropertyMock)
    @patch.object(media.File, "write_to_file", autospec=True)
    def test_download_song_by_index_downloads_correct_song(self, mocked_write_file, mocked_song):
        # test download song by referencing song index
        mocked_write_file.return_value = ""
        mocked_song.return_value = self.song_list[0]
        self.media.download(1)
        self.assertEqual(self.media.song, self.song_list[0])

    @patch.object(media.Media, "song", new_callable=PropertyMock)
    @patch.object(media.File, "write_to_file", autospec=True)
    def test_downloading_song_that_is_out_of_range_downloads_last_song(self, mocked_write_file, mocked_song):
        # test download song by referencing song index
        mocked_write_file.return_value = ""
        mocked_song.return_value = self.song_list[-1]
        self.media.download(100000)
        self.assertEqual(self.media.song, self.song_list[-1])

    @patch.object(media.Media, "song", new_callable=PropertyMock)
    @patch.object(media.File, "write_to_file", autospec=True)
    @patch.object(media, "Verbose", autospec=True)
    def test_download_song_by_song_name_downloads_correct_song(self, mocked_verbose, mocked_write_file, mocked_song):
        # test download song by referencing partial song mame
        mocked_write_file.return_value = ""
        mocked_song.return_value = self.song_list[0]
        self.media.download(self.song_list[0])
        self.assertEqual(self.media.song, self.song_list[0])
        mocked_verbose.assert_not_called()

    @patch.object(media.Media, "song", new_callable=PropertyMock)
    @patch.object(media.File, "write_to_file", autospec=True)
    @patch.object(media, "Verbose", autospec=True)
    def test_download_song_by_partial_song_name_downloads_correct_song(
        self, mocked_verbose, mocked_write_file, mocked_song
    ):
        # test download song by referencing partial song mame
        mocked_write_file.return_value = ""
        mocked_song.return_value = self.song_list[0]
        self.media.download(self.song_list[0][:3])
        self.assertEqual(self.media.song, self.song_list[0])
        mocked_verbose.assert_not_called()

    @patch.object(media.Media, "song", new_callable=PropertyMock)
    @patch.object(media.File, "write_to_file", autospec=True)
    @patch.object(media, "Verbose", autospec=True)
    def test_download_song_by_case_insensitive_name_downloads_correct_song(
        self, mocked_verbose, mocked_write_file, mocked_song
    ):
        # test download song is case-insensitive
        mocked_write_file.return_value = ""
        mocked_song.return_value = self.song_list[0]
        self.media.download(self.song_list[0][:3].upper())
        self.assertEqual(self.media.song, self.song_list[0])
        mocked_verbose.assert_not_called()

    @patch.object(media.Media, "song", new_callable=PropertyMock)
    @patch.object(media.File, "write_to_file", autospec=True)
    @patch.object(media, "Verbose", autospec=True)
    @patch.object(media.screen, "display_download_message", autospec=True)
    @patch.object(media.File, "get_human_readable_file_size", autospec=True)
    def test_download_song_method_work_correctly_with_parameters(
        self, mocked_size, mocked_screen, mocked_verbose, mocked_write_file, mocked_song
    ):
        mocked_write_file.return_value = ""
        mocked_song.return_value = self.song_list[0]
        mocked_size.return_value = "3MB"
        self.media.download(self.song_list[0], rename="new_name.mp3")

        self.assertEqual(self.media.song, self.song_list[0])
        mocked_verbose.assert_not_called()
        mocked_screen.assert_called_with(f"{self.artist_list[0]} - new_name.mp3", "3MB")

    def test_download_album_method_downloads_all_correct_songs(self):
        mp = media.Media(self.mix)
        mp.setMedia(1)
        tmp_dir = TempDir()
        mp.download_album(output=tmp_dir.name)
        self.assertEqual(mp.songs, self.song_list)

        album_dirname = " - ".join([self.artist_list[0], self.mixtape_list[0]])
        album_dirname = File.standardize_file_name(album_dirname)
        expected_dir = os.path.join(tmp_dir.name, album_dirname)

        self.assertTrue(os.path.isdir(expected_dir))
        songs_in_tmp_dir = os.listdir(expected_dir)
        self.assertEqual(len(songs_in_tmp_dir), len(self.song_list))

    def test_write_audio_method_return_correct_song_content(self):
        # test write audio method returns correct song content
        song_content = self.media._write_audio(self.song_list[0])
        self.assertEqual(song_content, self.get_song_content())

        song_content = self.media._write_audio(0)
        self.assertEqual(song_content, self.get_song_content())

    def test_write_audio_method_return_empty_result_when_track_not_found(self):
        # test write audio method raise MediaError when track not found by imdex
        results = self.unmocked_media._write_audio("abcdefg")
        self.assertIsNone(results)

    @patch.object(media.Media, "mp3_urls", new_callable=PropertyMock)
    @patch.object(media.Media, "_index_of_song", return_value=100, autospec=True)
    def test_write_audio_method_return_None_when_track_not_found(self, mocked_index, mocked_urls):
        mocked_urls.return_value = []
        audio = self.unmocked_media._write_audio(10)
        self.assertIsNone(audio)

    def test_media_cache_songs_that_have_already_been_played_or_download(self):
        cached_key = "-".join((self.artist_list[0], self.song_list[0]))
        self.media._cache_song(cached_key, self.get_song_content())

        cached_song = self.media._retrieve_song_from_cache(cached_key)
        self.assertEqual(cached_song, self.get_song_content())


class TestMediaPrivateMethod(BaseMediaTest):
    def test_media_index_of_song_method_with_integer_type(self):
        # test media index of song method with integer type
        self.assertEqual(self.media._index_of_song(1), 0)

    def test_media_index_of_song_method_raises_media_error_when_called_with_invalid_type(
        self,
    ):
        with self.assertRaises(MediaError) as context:
            self.media._index_of_song(object)
            self.assertEqual(context.exception.code, 5)
