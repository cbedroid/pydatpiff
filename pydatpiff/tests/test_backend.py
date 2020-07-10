import os
import sys 
import unittest
from unittest.mock import Mock,patch,PropertyMock
from ..errors import AlbumError
from ..backend import mediasetup,webhandler
from ..utils import request
from .test_utils import mockSessionResponse


class TestAlbum(unittest.TestCase):
    # create a dummy session
    dp_real_link = 'https://mobile.datpiff.com/mixtape/983402?trackid=1&platform=desktop'  

    text = '<blah blah blah>'
    json_data = {"sucess":True,'data':'foo-bar'}
    session = mockSessionResponse(
          status=200,
          text= text,
          json_data = json_data
    )

    mediasetup.Session = session
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
            self.assertEqual(error,self.dp.dpp_html)
            
    def test_datpiff_player_response(self):
        # test DatpiffPlayer response return correct request response 
        # when dpp_link is set correctly
        with patch.object(mediasetup,'Album',autospec=True) as dp:
            link = PropertyMock(return_value = self.dp_real_link)
            dp.dpp_link = link 
            dp.datpiff_player_response = PropertyMock(return_value=self.session.text)
            self.assertEqual(self.text ,dp.datpiff_player_response.return_value) 


        with patch.object(mediasetup.Album,'dpp_link',new_callable=PropertyMock) as link:
            # test DatpiffPlayer link is return correct value
            link.return_value = self.dp_real_link
            dp = self.dp
            dp.dpp_link = link
            self.assertEqual(self.dp_real_link,self.dp.dpp_link) 
         



