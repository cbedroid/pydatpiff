import os
import sys 
import unittest
from . import Mixtapes

class TestMixtapes(unittest.TestCase):
    def testCategory(self):
        """testing Mixtapes"""

        # testing category
        results = Mixtapes('hot').artists
        self.assertIsNotNone(results)

        # testing user input error fix
        results = Mixtapes('hkokodokwodjk').artists
        self.assertIsNotNone(results)

