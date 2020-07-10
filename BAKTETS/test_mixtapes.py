import os
import sys 
import unittest
from unittest.mock import Mock,patch
from ...pydatpiff import mixtapes 
from ...pydatpiff import media


class TestMixtapes(unittest.TestCase):
    def testCategory(self):
        """testing Mixtapes"""
        # testing category
        results = mixtapes.Mixtapes('hot').artists
        self.assertIsNotNone(results)

    @patch.object(mixtapes.Mixtapes,'_Start')
    def test_start_function(self,start):
        start(start='lil wayne')
        mix = mixtapes.Mixtapes
        start.assert_called_once()
        start.assert_called_once_with(start='lil wayne')
     

    @patch.object(mixtapes.Mixtapes,'_Start')
    def test_start_function(self,start):
        start(start='lil wayne')
        mix = mixtapes.Mixtapes
        start.assert_called_once()
        start.assert_called_once_with(start='lil wayne')
        
    
media_dummy = mixtapes.Mixtapes.__class__('mixtapes.Mixtapes.Dummy',
                                    (mixtapes.Mixtapes,),
                                    {})

class TestMedia(unittest.TestCase):
    @patch.object(media.Media,'findSong')
    def test_find_Song(self,finder):
        pass



     
        
