import os
import sys
import unittest
from unittest.mock import Mock, patch, PropertyMock
from ...errors import AlbumError
from ...backend import mediasetup, webhandler
from ...utils import request
from ..test_utils import mockSessionResponse


dp_real_link = "https://mobile.datpiff.com/mixtape/983402?trackid=1&platform=desktop"
dummy_text = "<blah blah blah>"
dummy_json_data = {"success": True, "data": "foo-bar"}

mocked_session = mockSessionResponse(
    status=200, text=dummy_text, json_data=dummy_json_data
)


class TestDatpiffPlayerProperties(unittest.TestCase):
    # MOCKS

    def setUp(self):
        # PATCHES
        self.session = patch.object(
            mediasetup, "Session", return_value=mocked_session.text
        )
        self.media_scrape = patch.object(mediasetup, "MediaScrape", autospec=True)
        self.album = patch.object(mediasetup, "Album", autospec=True)

        # PATCH CLASS
        self.SESSION = self.session.start()
        self.MS = self.media_scrape.start()
        self.ALBUM = self.album.start()
        self.addCleanup(patch.stopall)

    def test_DatpiffPlayer_has_bio(self):
        # * check for Re Group Error AttributeError
        # - Cause: RE cannot find pattern in string
        # - Return: RE group(1)

        with self.assertRaises(AttributeError) as error:
            album = self.album("blah")
            album.bio()

        # given a proper Re pattern for MediaScrape.getBio,
        # check if Abum.bio is now returning value

        bio = PropertyMock(return_value="blah")
        album = self.album
        album.bio = bio
        album("blah")
        self.assertEqual("blah", album.bio())


class TestAlbum(unittest.TestCase):
    # create a dummy session
    mediasetup.Session = mocked_session
    link = "https://www.google.com"
    dp = mediasetup.Album(link)

    def test_Album_initialized_with_url_link(self):
        pass

    def test_datpiff_player_switch_to_mobile_on_error(self):
        # return random html to throw error

        # should assert True became album name is not populated
        self.assertTrue(self.dp.USE_MOBILE)

    def test_datpiff_player_has_response_text(self):
        # since the mock Session return <blah blah blah>
        # regex group should throw Attribute error here
        with self.assertRaises(AttributeError) as error:
            self.assertEqual(error, self.dp.dpp_html)

    def test_datpiff_player_response(self):
        # test DatpiffPlayer response return correct request response
        # when dpp_link is set correctly
        with patch.object(mediasetup, "Album", autospec=True) as dp:
            link = PropertyMock(return_value=dp_real_link)
            dp.dpp_link = link
            dp.datpiff_player_response = PropertyMock(return_value=mocked_session.text)
            self.assertEqual(dummy_text, dp.datpiff_player_response.return_value)

        with patch.object(
            mediasetup.Album, "dpp_link", new_callable=PropertyMock
        ) as link:
            # test DatpiffPlayer link is return correct value
            link.return_value = dp_real_link
            dp = self.dp
            dp.dpp_link = link
            self.assertEqual(dp_real_link, self.dp.dpp_link)


class TestMP3Class(unittest.TestCase):
    mediasetup.Session = mocked_session
    Mp3 = mediasetup.Mp3(mocked_session)
    songs_value = ["mp3_1", "mp3_2", "mp3_3", "mp3_4", "mp3_5"]

    def test_mp3_has_value(self):
        # check if Mp3.songs are being populated
        with patch.object(mediasetup, "MediaScrape", autospec=True) as MS:
            MS.find_song_names = Mock(return_value=self.songs_value)
            # mp3 = mediasetup.Mp3(mocked_session)
            self.assertEqual(self.songs_value, self.Mp3.songs)

            # test Mp3.songs datatype is a list
            self.assertIsInstance(self.Mp3.songs, list)

    def test_mp3Url_format_correct(self):
        with patch.object(mediasetup, "Mp3", autospec=True) as MP3:
            values = ["blah%20blah%20", "12345"]
            prefix = "https://hw-mp3.datpiff.com/mixtapes/"
            encoder = PropertyMock(return_value=values[0])
            ID = PropertyMock(return_value=values[1])
            MP3.urlencode_track = encoder
            MP3.AlbumId = ID
            mp3 = mediasetup.Mp3(mocked_session)
            mp3.mp3Urls = PropertyMock(return_value="".join((prefix, *(values))))
            self.assertIn(prefix, mp3.mp3Urls.return_value)
