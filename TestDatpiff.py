import os
import sys
import unittest
from src.mixtapes import Mixtapes
from src.urls import Urls

class TestMixtapes(unittest.TestCase):
    def testCategory(self):
        """testing for correct category"""
        mix = Mixtapes('hot')
        results = mix.artists
        self.assertIsNotNone(results)
