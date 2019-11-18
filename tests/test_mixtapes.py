import os
import sys 
import unittest
from unittest.mock import Mock,patch
from ..src import mixtapes as mt

class TestMixtapes(unittest.TestCase):
    def testCategory(self):
        """testing Mixtapes"""
        # testing category
        results = mt.Mixtapes('hot').artists
        self.assertIsNotNone(results)
        

    # testSearch
    @patch.object(mt, "Mixtapes")
    def test_if_search_has_a_response(self,instance):
        instance.return_value = 'Lil Wayne'
        mix = mt.Mixtapes()
        print(instance.mock_calls)

        

