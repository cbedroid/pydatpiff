import unittest
from unittest.mock import Mock, patch

from pydatpiff import media as md
from pydatpiff import mixtapes as mt
from pydatpiff.errors import MediaError, MixtapesError
from pydatpiff.mixtapes import Mixtapes
from pydatpiff.utils import request
from tests.test_utils import mockSessionResponse, run_mix

Session = request.Session
Session.TIMEOUT = 180

mix = run_mix("hot")


class TestMixtapes(unittest.TestCase):
    def test_category_is_set_correct(self):
        # testing category
        results = mix.artists
        self.assertIsNotNone(results)

    @patch.object(Mixtapes, "_selectMixtape")
    def test_start_function(self, start):
        start(start="lil wayne")
        start.assert_called_once_with(start="lil wayne")

    def test_mixtapes_attributes_length(self):
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
    REAL_MIX = mt.Mixtapes("hot", limit=1)

    def setUp(self):
        mt.Session.method = Mock(return_value=mockSessionResponse())
        self.mocked_mix = mt.Mixtapes
        self.mocked_mix._setup = Mock()
        self.attrs = ["mixtapes", "artists", "links", "views", "album_covers"]

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

    def populate_Mixtapes(self, mix, total):
        with patch.object(mt.DOMProcessor, "findRegex") as find_regex:
            mix._mixtape_resp = mockSessionResponse()

            data = ["artist_%s" % x for x in range(total)]
            find_regex.return_value = data
            mix._setMixtapesAttributes()
            return mix

    # Setup End

    def test_Mixtapes__str__(self):
        mix = mt.Mixtapes("hot")
        classname = mix.__class__.__name__
        self.assertTrue(classname in str(mix))

    def test_Mixtapes__repr__(self):
        # test by category
        by_category_mix = mt.Mixtapes("popular")
        self.assertTrue("popular" in repr(by_category_mix))
        self.assertFalse("search" in repr(by_category_mix))

        by_search_mix = mt.Mixtapes(search="Tupac")
        self.assertTrue(all(x in repr(by_search_mix) for x in ["Tupac", "search"]))
        self.assertFalse("popular" in repr(by_search_mix))

    def test_mixtapes_response_status_equal_200(self):
        mixtapes = self.get_Mixtapes("hot")
        # self.Mixtapes = mixtapes
        search = mixtapes._selectMixtape("blah")
        print(search.status_code)

        self.assertEqual(search.status_code, 200)
        self.assertEqual(search.text, "content here")

    def test_Mixtapes__len__(self):
        mix = self.get_Mixtapes("exclusive")
        # test if there are no artists, len return 0
        self.assertTrue(len(mix) == 0)

        # test if there are artists, len return the numbers of artists
        mix = self.populate_Mixtapes(mix, 20)
        self.assertTrue(len(mix) != 0)

        # test if all attribute length are the same as artist length
        for attr in self.attrs:
            attr = getattr(mix, attr, [])
            self.assertTrue(len(attr) == 20)

    def test_Mixtapes_attributes_return_correct_value(self):
        mix = self.get_Mixtapes("exclusive")
        mix = self.populate_Mixtapes(mix, 20)
        self.assertEqual(mix.artists[0], "artist_0")

        # test if links are vaild url links
        real_links = self.REAL_MIX.links
        self.assertTrue(all(link.endswith(".html") for link in real_links))

    def test_mixtapes_clean_method_filter_datatypes_correctly(self):
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

    def test_mixtapes_setMixtapesAttributes_method_set_attributes_correctly(
        self,
    ):
        mix = mt.Mixtapes("hot")
        for attr in self.attrs:
            var = getattr(mix, attr, None)
            self.assertEqual(var, None)

        resp = mix = mt.Mixtapes("hot")
        resp._mixtape_resp = mockSessionResponse()

        # test if all attributes are set correctly using regexwhen
        # check if attributes now have values
        with patch.object(mt.DOMProcessor, "findRegex") as find_regex:
            mix._mixtape_resp = mockSessionResponse()
            find_regex.return_value = "successful"
            mix._setMixtapesAttributes()

            for attr in self.attrs:
                var = getattr(mix, attr, None)
                self.assertEqual(var, "successful")

    def test_Mixtapes_selection_return_correct_mixtape(self):
        mix = mt.Mixtapes("new")

        # test if exception is thrown when Mixtapes attribute is not set or is None
        with patch.object(mt.Selector, "select_from_index") as user_selection:
            # user_select.side_effect = MixtapesError(1)
            user_selection.return_value = None
            with self.assertRaises(MixtapesError):
                mix._select(3)
                user_selection.assert_called_with(1)

        mix = self.populate_Mixtapes(mix, 50)
        selection = mix._select(3)

        # NOTE: by default Mixtapes._selection returns selection - 1
        # zero (0) is skipped by default

        # test by inputting a numerical(int) value
        self.assertEqual(selection, 2)

        # test by inputting a String (str) value
        """NOTE That populate_Mixtapes method return an list.
             Its first string is 'artist_0' although zero when using a numerical parameter,
             using string (str) will discard this behavior and follow python's traditional
             list indexing
             Ex: populated_Mixtapes --> [artist_0, artist_1...etc]
         """
        selection = mix._select("artist_2")
        self.assertEqual(selection, 2)

        # testing Mixtapes.display method passes
        mix.display()


md.Session.method = Mock(return_value=mockSessionResponse())
md.Tmp = Mock(autospec=True)
md.Tmp.removeTmpOnStart = Mock(return_value=True)
md.Tmp.create = Mock(return_value="dummy file")


def populate_Mixtapes(mix, total):
    with patch.object(mt.DOMProcessor, "findRegex") as find_regex:
        mix._mixtape_resp = mockSessionResponse()

        data = ["artist_%s" % x for x in range(total)]
        find_regex.return_value = data
        mix._setMixtapesAttributes()
        return mix


######################
####  MEDIA  TEST ####
######################


class TestMedia(unittest.TestCase):
    def setUp(self):
        mt.Session.method = Mock(return_value=mockSessionResponse())
        mocked_mix = mt.Mixtapes
        mocked_mix._setup = Mock()

        # Unpopulated Mixtapes
        category_mix = mocked_mix(category="hot")
        search_mix = mocked_mix(search="Tupac")

        # Populating attributes for both search and category Mixtape
        self.cp_mix = populate_Mixtapes(category_mix, 10)
        self.cp_mix = populate_Mixtapes(search_mix, 10)

        self.MEDIA = md.Media(self.cp_mix)

    def populate_Mixtapes(self, mix, total):
        with patch.object(md.Mixtapes.DOMProcessor, "findRegex") as find_regex:
            mix._mixtape_resp = mockSessionResponse()

            data = ["artist_%s" % x for x in range(total)]
            find_regex.return_value = data
            mix._setMixtapesAttributes()
            return mix

    def test_TMP_is_patched(self):
        self.assertTrue(md.Tmp.create() == "dummy file")

    def test_Media_str_method_is_correct(self):
        self.assertIn(self.cp_mix.__class__.__name__, str(self.MEDIA))
        self.assertIn("Media", str(self.MEDIA))

    def test_Media_repr_method_is_correct(self):
        self.assertIn(self.cp_mix.__class__.__name__, repr(self.MEDIA))

    def test_Media_len_method(self):
        pass
        # self.assertEqual(len(self.MEDIA), 10)

    def test_if_media_player_is_created(self):
        media = md.Media(self.cp_mix)
        self.assertIsNotNone(media.player)

        # test if player is updated when reinitializing Media
        old_player = media.player
        new_media = md.Media(self.cp_mix, player="MPV")
        new_player = new_media.player
        self.assertFalse(old_player == new_player)

    def test_Media_initialization(self):
        # "__downloaded_song" is not tested because it is private variable
        # It will be tested in backend

        # test MediaError is thrown when mixtapes is not passed in init
        with self.assertRaises(MediaError):
            md.Media()
            # test if error is thrown if "mixtapes" parameter is not an object of Mixtapes class
            md.media(mixtape="blah")

        # test whether setMedia is called when "pre_selection" keyword is passed
        with patch.object(md.Media, "setMedia") as SM:
            md.Media(self.cp_mix, 3)
            SM.assert_called_once_with(3)

        # test setup method set attributes on init
        attrs = [
            "_session",
            "_Mixtapes",
            "_artist_name",
            "_album_name",
            "_current_index",
            "_selected_song",
        ]
        media = md.Media(self.cp_mix)
        with patch.object(md.Media, "setup") as setup:
            media.setup(self.cp_mix)
            for attr in attrs:
                self.assertTrue(hasattr(media, attr))
        setup.assert_called_once_with(self.cp_mix)

    def test_findSong_returns_correct_data(self):
        media = md.Media(self.cp_mix)
        with patch.object(md, "Queued") as Q:
            ret = [
                {"ablumNo": 1, "album": "mixtape_1", "song": "song_1"},
                {"ablumNo": 2, "album": "mixtape_2", "song": "song_2"},
                {"ablumNo": 3, "album": "mixtape_3", "song": "song_3"},
            ]

            Q.run = Mock(return_value=ret)

            # patch Datatype helper class and methods
            md.Object = Mock()
            md.Object.removeNone = Mock(return_value=ret)

            songs_found = media.findSong("mixtape")
            songs_len = len(songs_found)
            self.assertEqual(songs_len, 3)

        self.assertTrue(len(media._Mixtapes.links) > 2)
