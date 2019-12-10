import os
import sys 
import unittest
from unittest.mock import Mock,patch
from datpiff import mixtapes as mt


class TestMixtapes(unittest.TestCase):
    def testCategory(self):
        """testing Mixtapes"""
        # testing category
        results = mt.Mixtapes('hot').artists
        self.assertIsNotNone(results)

    @patch.object(mt.Mixtapes,'_Start')
    def test_start_function(self,start):
        start(start='lil wayne')
        mix = mt.Mixtapes
        start.assert_called_once()
        start.assert_called_once_with(start='lil wayne')
     
    @patch.object(mt.Mixtapes,'_Start')
    def test_start_function(self,start):
        start(start='lil wayne')
        mix = mt.Mixtapes
        start.assert_called_once()
        start.assert_called_once_with(start='lil wayne')
        
     
        

    # testSearch
    @patch.object(mt, "Mixtapes")
    def test_if_search_has_a_response(self,instance):
        instance.return_value = 'Lil Wayne'
        mix = mt.Mixtapes()
        print(instance.mock_calls)

        

