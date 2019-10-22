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
