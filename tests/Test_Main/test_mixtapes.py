import os

import sys
import unittest
import json
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from tests.test_utils import mockSessionResponse, Fake_Session_Mock
from tests.test_utils import run_mix
from pydatpiff.mixtapes import Mixtapes, Session
from pydatpiff.utils import request
from pydatpiff.errors import MixtapesError
from pydatpiff import mixtapes as mt

Session = request.Session
Session.TIMEOUT = 180

mix = run_mix("hot")
# search_mix = run_mix(search="jay-z")


class TestMixtapes(unittest.TestCase):
    # Mixtapes._session = PropertyMock(return_value=mockSessionResponse)

    def test_category_set_correct(self):
        # testing category
        results = mix.artists
        self.assertIsNotNone(results)

    @patch.object(Mixtapes, "_selectMixtape")
    def test_start_function(self, start):
        start(start="lil wayne")
        # mix = self.mix
        # start.assert_called_once()
        start.assert_called_once_with(start="lil wayne")

    def test_if_mixtapes_has_attributes(self):
        assert hasattr(mix, "artist") == False
        self.assertEqual(len(mix.artists), 12)
        self.assertEqual(len(mix.links), 12)
        self.assertEqual(len(mix.views), 12)

    @patch.object(Mixtapes, "artists", autospec=True)
    def test_class__len__returns_correct_length(self, MT):
        MT.return_value = ["Jay-z", "Lil wayne", "1", "2", "3", "4"]
        self.assertEqual(len(mix.artists.return_value), 6)

    def test_search_method_return_correct_artist(self):
        session = mix._session
        session.method = Mock(return_value="Jay-Z")
        results = mix._search_for("anything")
        self.assertEqual(results, "Jay-Z")

    def test_empty_search_return_None(self):
        # testing for serch to return None value
        results = mix._search_for("")
        self.assertEqual(results, None)

    @patch.object(Mixtapes, "artists", autospec=True)
    def test_artist_found_length(self, MT):
        MT.return_value = ["Jay-z", "Lil wayne", "1", "2", "3", "4"]
        self.assertEqual(len(mix.artists.return_value), 6)

    @patch.object(Mixtapes, "_search_for", autospec=True)
    def test_search_function_called_once(self, MT):
        session = mix._session
        session.method = Mock(return_value="Jay-Z")
        MT.return_value = None
        mix._selectMixtape(search="Jay-Z")
        count = MT.call_count
        self.assertEqual(count, 1)


class TestMixtapes2(unittest.TestCase):
    mt.Session.method = Mock(return_value=mockSessionResponse())
    mocked_mix = mt.Mixtapes
    mocked_mix._setup = Mock()

    def get_Mixtapes(self, category, **kwargs):
        if kwargs:
            return self.mocked_mix(kwargs)
        return self.mocked_mix(category)

    @property
    def Mixtapes(self):
        return self.mocked_mix

    @Mixtapes.setter
    def Mixtapes(self, obj):
        self.mocked_mix = obj

    def test_mixtapes_response_equal_200(self):
        mixtapes = self.get_Mixtapes("hot")
        # self.Mixtapes = mixtapes
        search = mixtapes._selectMixtape("blah")
        print(search.status_code)

        self.assertEqual(search.status_code, 200)
        self.assertEqual(search.text, "content here")

    def test_mixtapes_clean(self):
        mix = self.Mixtapes
        data = "Jay-z       "
        resp = mix._clean(data, expected=str)

        # test return when_str_is_passed
        self.assertEqual(resp, "Jay-z")

        # test Exception raised when data length less than 3 characters
        with self.assertRaises(MixtapesError):
            mix._clean("12", expected=str)

        # test Exception raised when passed incorrect datatype
        with self.assertRaises(MixtapesError):
            mix._clean("this is a string", expected=dict)

    def test_mixtapes_setMixtapesAttributes(self):
        mix = mt.Mixtapes("hot")
        attrs = ["mixtapes", "artists", "links", "views", "album_covers"]
        for attr in attrs:
            var = getattr(mix, attr, None)
            self.assertEqual(var, None)

        resp = mix = mt.Mixtapes("hot")
        resp._mixtape_resp = mockSessionResponse()

        # test Exception raised when regex not found in request reponse
        with self.assertRaises(MixtapesError):
            resp._setMixtapesAttributes()
            resp.artists = "blah"

        # test if all attributes are set correctly using regexwhen
        # check if attributes now have values
        with patch.object(mt.DOMProcessor, "findRegex") as find_regex:
            mix._mixtape_resp = mockSessionResponse()
            find_regex.return_value = "successful"
            mix._setMixtapesAttributes()
            artists = mix.artists

            for attr in attrs:

                var = getattr(mix, attr, None)
                self.assertEqual(var, "successful")

    # def test_searchTree_was_called(self):
    #     mix = mt.Mixtapes("hot")
    #     with patch.object(
    #         mt,'Mixtapes'
    #     ) as search_tree:
    #         with patch.object(mt.DOMProcessor, "findRegex") as find_regex:
    #             mix._mixtape_resp = mockSessionResponse()
    #             find_regex.return_value = "successful"
    #             mix._setMixtapesAttributes()
    #             artists = mix.artists

    #             mix._mixtape_resp = mockSessionResponse()
    #             find_regex.return_value = "successful"
    #             mix._setMixtapesAttributes()

    #             # test searchTree was called
    #             mix.artists = "Lil Wayne"
    #             search_tree.assert_called()
