import os
import sys 
import unittest
from unittest.mock import Mock,patch
from ..test_utils import run_media, mockSessionResponse
from ...errors import AlbumError
from ...backend import mediasetup,webhandler
from ...utils import request

media = run_media()
Session = request.Session
Session.TIMEOUT = 180

class TestBackend(unittest.TestCase):
    EP = mediasetup.EmbedPlayer(link='foo')

    def test_embedplayer_mix_link_response(self):

        with patch.object(Session,"method") as method:
            response = mockSessionResponse(text='embed_link')
            method.return_value = response 
            mix_link = self.EP.mix_link_response
            self.assertEqual(mix_link,"embed_link")


    def test_embed_player_media_ID_return_correct_type_and_data(self):
        """
         Next we will try to get the media Album ID number
         First thing to do is get backend.webhandler.MediaScrape class
         Then we will mock this class and attributes, and finally call
         EP (embed_player class object using it (MediaScrape)
        """
        with patch.object(Session,"method") as method:
            response = mockSessionResponse(text='embed_link')
            method.return_value = response 

            with patch.object(webhandler.MediaScrape,
                        "get_suffix_number",string='nothing') as suffix:

                suffix.return_value = None
                self.assertEqual(self.EP.album_ID,None)

                #testing the datatype       
                suffix.return_value = ["12345"]
                self.assertEqual(type(self.EP.album_ID),list)

                # testing return data
                self.assertEqual(self.EP.album_ID,['12345'])
    
    """
    def test_embed_player_has_correct_response(self):
        method = self.SESSION_METHOD
        response = mockSessionResponse(text='a lot of data',status=200)
        method.return_value = response 

        #self.EP.create_player_url = Mock(return_value="https://nothing.com")
        player_response = self.EP.player_response
        self.assertEqual(player_response.text,"a lot of data")
        self.assertEqual(player_response.status_code,200)
    """


