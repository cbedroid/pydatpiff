import re
from unittest import TestCase
from unittest.mock import Mock, patch

from pydatpiff import media, mixtapes
from pydatpiff.errors import MediaError
from tests.utils import BaseTest


class VLCPlayer:
    pass


class MPV:
    pass


class IncompatiblePlayerError(Exception):
    pass


class TestMedia(BaseTest, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # mocked mixtapes
        mix_content = cls.get_request_content("mixtape")
        mix_method = mixtapes.Session.method = Mock(autospec=True)
        mix_method.return_value = cls.mocked_response(content=mix_content)
        cls.mix = mixtapes.Mixtapes()

        # mocked media
        cls.content = cls.get_request_content("media")
        cls.method = media.Session.method = Mock(autospec=True)
        cls.method.return_value = cls.mocked_response(content=cls.content)
        cls.media = media.Media(cls.mix)
        cls.media.setMedia(1)

        # Add test artist and album (mixtape)
        cls.test_artist = cls.artist_list[0]
        cls.test_album = cls.mixtape_list[0]

    def test_media_raises_an_exception_when_mixtape_is_not_a_valid_mixtape_type(self):
        with self.assertRaises(MediaError):
            media.Media(object)

    @patch.object(media.Player, "getPlayer")
    def test_media_player_parameters_is_a_valid_media_player_type(self, mocked_get_player):
        mocked_get_player.return_value = VLCPlayer()
        my_media = media.Media(self.mix, player="vlc")
        self.assertEqual(mocked_get_player.call_count, 1)
        self.assertEqual(my_media.player.__class__, VLCPlayer)

        mocked_get_player.return_value = MPV()
        my_media = media.Media(self.mix, player="mpv")
        self.assertEqual(mocked_get_player.call_count, 2)
        self.assertEqual(my_media.player.__class__, MPV)

    def test_media_len_method_return_correct_length(self):
        self.assertEqual(len(self.media), len(self.song_list))

    @patch.object(media.ThreadQueue, "execute", autospec=True)
    def test_media_find_song_return_albums(self, queue):
        query_result = {
            "index": 1,
            "album": "A Gangsta's Pain: Reloaded",
            "song": "Switches  Dracs (feat. Lil Durk  EST Gee)",
        }
        queue.return_value = [query_result]
        response = self.media.find_song("Switches")
        self.assertIn(query_result, response)

    def test_media_album_is_correct(self):
        album = self.test_album
        self.assertEqual(album, self.media.album.name)

    def test_media_artist_is_correct(self):
        self.assertEqual(self.test_artist, self.media.artist)

    def test_media_album_cover_url_was_created(self):
        album_cover = self.media.album_cover
        self.assertIsNotNone(album_cover)

        # test album name is in  album cover url
        filter_character = re.sub(r"[^\w\s]", "", self.test_album)
        url_encoded_name = re.sub(r"\s", "_", filter_character)
        self.assertIn(url_encoded_name, album_cover)

    def test_media_songs_are_correct(self):

        # test song is in media album
        songs = self.media.songs
        self.assertIn(self.song_list[0], songs)
        # test songs total is correct
        self.assertCountEqual(self.song_list, songs)

    # @patch.object(media.File, "write_to_file")
    # @patch.object(media.Media, "_write_audio")
    # def test_media_download_song_from_song_index(self, write_file, write_audio):
    #     write_audio.return_value = b"song content"
    #     self.media.download(0)
    #
    #     songname = " - ".join((self.media.artist, self.song_list[0].strip() + ".mp3"))
    #     songname = media.File.join(os.getcwd(), download_path)
    #     write_file.assert_called_once()
    #     write_file.assert_called_with(
    #         download_path, b"song content", mode="wb"
    #       )
