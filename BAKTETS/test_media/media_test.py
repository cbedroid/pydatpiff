import os
import sys 
import unittest
from unittest.mock import Mock,PropertyMock,patch
from ..test_utils import run_media
from ...backend import mediasetup,webhandler
from ...errors import MediaError
from ...utils import request

"""
media_dummy = mixtapes.Mixtapes.__class__('mixtapes.Mixtapes.Dummy',
                                    (mixtapes.Mixtapes,), {})
"""
media = run_media()

Session = request.Session
Session.TIMEOUT = 180

class TestMedia(unittest.TestCase):
    def test_media_setMedia_fails(self):
        with patch.object(media,'setMedia',side_effect=MediaError(1)) as SM:
            self.assertRaises(MediaError,SM,1)

    def test_media_artist_name_is_set_correct(self):
        with patch.object(media,'setMedia',selection = 0) as setter:
            with patch.object(media,'_artist_name',"Jay-Z") as artist:
                self.assertEqual(media.artist,'Jay-Z')
                
            with patch.object(media,'_artist_name',"Lil Wayne") as artist:
                self.assertNotEqual(media.artist,'Jay-Z')
                self.assertEqual(media.artist,'Lil Wayne')


    def test_media_album_name_is_set_correct(self):
        with patch.object(media,'setMedia',selection = 0) as setter:
            with patch.object(media,'_album_name',"The Carter") as artist:
                self.assertEqual(media.album,'The Carter')



                
