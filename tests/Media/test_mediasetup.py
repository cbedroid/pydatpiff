from unittest.mock import Mock, PropertyMock, patch

from pydatpiff.backend import mediasetup
from pydatpiff.backend.mediasetup import Album, DatpiffPlayer
from tests.utils import BaseTest


class TestAlbum(BaseTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # mocked session
        session = Album._session = Mock(autospec=True)
        cls.method = session.method = Mock(autospec=True)
        cls.media_request_content = cls.get_request_content("media")
        cls.method.return_value = cls.mocked_response(content=cls.media_request_content)

        # mock mediasetup Album's embed player response
        mocked_embed_player_response = cls.get_request_content("embed_player")
        mediasetup_session = mediasetup.Session.method = Mock(autospec=True)
        mediasetup_session.return_value = cls.mocked_response(content=mocked_embed_player_response)

        # Set the testing Album
        link = cls.mixtape_links[0]
        cls.album = Album(link=link)

    def test_datpiff_player_raise_not_implemented_error_when_called_as_standalone(self):
        with self.assertRaises(NotImplementedError):
            DatpiffPlayer("https://www.datpiff.com/album/some-link")

    def test_album_initializes_correctly(self):
        # test album name is set on initialization
        self.assertIsNotNone(self.album.name)

    @patch.object(DatpiffPlayer, "_verify_version", autospec=True)
    def test_datpiff_version_set_version_correctly(self, mocked_get_version):
        mocked_get_version.return_value = None
        album = Album(link=self.mixtape_links[0])
        self.assertEqual(album._USE_MOBILE_VERSION, True)

        mocked_get_version.return_value = "some-version"
        album = Album(link=self.mixtape_links[0])
        self.assertEqual(album._USE_MOBILE_VERSION, False)

    def test_build_web_player_url_method_creates_embed_player_url_correctly(self):
        album_id = "1015177"
        embed_player_url = self.album.build_web_player_url(album_id)
        expected_url = f"https://embeds.datpiff.com/mixtape/{album_id}?trackid=1&platform=desktop"
        self.assertEqual(embed_player_url, expected_url)

    def test_album_name_is_set_property(self):
        album = Album(link=self.mixtape_links[0])
        album.name = "some-name"
        self.assertEqual(album.name, "some-name")

        album.name = "some-other-name"
        self.assertEqual(album.name, "some-other-name")

    def test_album_id_is_extracted_properly_from_album_link(self):
        # test album id is extracted from album link
        # Note: For list of album IDs, see tests/utils/test_utils.py
        album = Album(link=self.mixtape_links[0])
        self.assertEqual(album._album_ID, "1015177")

        album = Album(link=self.mixtape_links[1])
        self.assertEqual(album._album_ID, "1015203")

    def test_mocked_uploader_name_returns_correct_uploader_name(self):
        # test uploader bio is set correctly
        self.assertEqual(self.album.uploader, "flybeats09")

    def test_mocked_uploader_bio_is_set_correctly(self):
        # test uploader bio is set correctly
        expected_bio = "A Gangsta's Pain: Reloaded Mixtape by Moneybagg Yo"
        self.assertEqual(self.album.bio, expected_bio)

    def test_album_html_property_method_returns_album_response_content(self):
        # test album html property method returns the correct
        # album response content from  album link
        self.assertEqual(self.album._album_html, self.media_request_content)

    @patch.object(mediasetup.Mp3, "songs", new_callable=PropertyMock)
    def test_lookup_song_method_return_correct_song(self, mocked_songs):
        # test lookup song method returns correct song
        mocked_songs.return_value = self.song_list
        index_and_links = (1, self.mixtape_links[0])
        song = self.album.lookup_song(links=index_and_links, song="Switches")
        self.assertEqual(
            song,
            {
                "index": 1,
                "album": self.album.name,
                "song": self.song_list[0],
            },
        )
