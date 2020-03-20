import os
import sys 
import unittest
import json
from unittest.mock import Mock,patch
from ..test_utils  import run_mix  
from ...mixtapes import Mixtapes
from ...utils import request

Session = request.Session
Session.TIMEOUT = 180

mix = run_mix()
class TestMixtapes(unittest.TestCase):


    def test_category_set_correct(self):
        # testing category
        results = mix.artists
        self.assertIsNotNone(results)

    @patch.object(Mixtapes,'_Start')
    def test_start_function(self,start):
        start(start='lil wayne')
        #mix = self.mix
        start.assert_called_once()
        start.assert_called_once_with(start='lil wayne')

    def test_if_mixtapes_has_attributes(self):
        assert hasattr(mix,"artist") == False
        self.assertEqual(len(mix.artists),12)
        self.assertEqual(len(mix.links),12)
        self.assertEqual(len(mix.views),12)


    @patch.object(Mixtapes,"artists",autospec=True)
    def test_artist_found_length(self,MT):
        MT.return_value=['Jay-z','Lil wayne','1','2','3','4']
        self.assertEqual(len(mix.artists.return_value),6)


    def test_search_has_results(self):
        session = mix._session
        session.method = Mock(return_value="Jay-Z") 
        results = mix.search('anything')
        self.assertEqual(results ,'Jay-Z')


    def test_search_parameters(self):
        #testing for serch to return None value
        results = mix.search('')
        self.assertEqual(results ,None)

