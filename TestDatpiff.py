import os
import sys
import unittest
from src.mixtapes import Mixtapes

class TestMixtapes(unittest.TestCase):
    def testCategory(self):
        """testing for correct category"""
        results = Mixtapes('hot').artists
        self.assertIsNotNone(results, None)
