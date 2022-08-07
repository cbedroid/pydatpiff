from unittest import TestCase
from unittest.mock import Mock

from pydatpiff import mixtapes
from pydatpiff.errors import MixtapesError
from tests.test_utils import BaseTest


class TestMixtapes(BaseTest, TestCase):
    def setUp(self):
        content = self.get_request_content("mixtape")
        request = mixtapes.Session.method = Mock(autospec=True)
        request.return_value = self.mocked_response(content=content)
        self.mix = mixtapes.Mixtapes()

    def test_mixtape_initialization_method(self):

        content = self.get_request_content("mixtape")
        session = mixtapes.Session.method = Mock(autospec=True)
        session.return_value = self.mocked_response(content=content)
        mix = mixtapes.Mixtapes(category="some_random_category", limit=20)

        # test mocked session was called
        mix._session.method.assert_called()

        mix_len = len(mix)
        self.assertEqual(mix_len, 12)

        mix._artists = None
        mix_len = len(mix)
        self.assertEqual(mix_len, 0)

        # testing len method with artists attribute
        del mix._artists
        mix_len = len(mix)
        self.assertEqual(mix_len, 0)

    def test_mixtape_mixtapes_were_set(self):
        mixtapes = self.mix.mixtapes
        total_mixtapes = len(mixtapes or [])
        self.assertGreater(total_mixtapes, 0)

        del self.mix._mixtapes
        self.assertIsNone(self.mix.mixtapes)

    def test_mixtape_artists_were_set(self):
        artists = self.mix.artists
        total_artists = len(artists or [])
        self.assertGreater(total_artists, 0)

        del self.mix._artists
        self.assertIsNone(self.mix.artists)

    def test_mixtape_links_were_set(self):
        links = self.mix.links
        total_links = len(links or [])
        self.assertGreater(total_links, 0)

        del self.mix._links
        self.assertIsNone(self.mix.links)

    def test_mixtape_views_were_set(self):
        views = self.mix.views
        total_views = len(views or [])
        self.assertGreater(total_views, 0)

        del self.mix._views
        self.assertIsNone(self.mix.views)

    def test_mixtape_rating_were_set(self):
        total_ratings = len(self.mix.ratings or [])
        self.assertGreater(total_ratings, 0)

        del self.mix._ratings
        self.assertIsNone(self.mix.ratings)

    def test_mixtape_album_cover_were_set(self):
        album_covers = self.mix.album_covers
        total_covers = len(album_covers or [])
        self.assertGreater(total_covers, 0)

        del self.mix._album_covers
        self.assertIsNone(self.mix.album_covers)

    def test_mixtape_attributes_size_maps_to_artist_attribute_size(self):
        mixtapes_attributes = ["mixtapes", "links", "views", "album_covers"]
        mix = self.mix
        artist_length = len(mix.artists)

        for attr in mixtapes_attributes:
            obj = getattr(mix, attr, [])
            if not obj:
                raise AttributeError("Mixtape does not have attribute: {}".format(obj))
            attr_length = len(obj)
            self.assertEqual(artist_length, attr_length)

    def test_mixtapes_includes_correct_mixtape(self):
        test_mixtape = self.mixtape_list[0]
        mixtapes = self.mix.mixtapes
        self.assertIn(test_mixtape, mixtapes)

        mixtape_name = mixtapes[mixtapes.index(test_mixtape)]
        self.assertEqual(mixtape_name, "A Gangsta's Pain: Reloaded")

    def test_artists_includes_correct_artist(self):
        test_artist = self.artist_list[0]
        artists = self.mix.artists
        self.assertIn(test_artist, artists)

        artist_name = artists[artists.index(test_artist)]
        self.assertEqual(artist_name, "Moneybagg Yo")

    def test_category_defaults_to_hot_when_category_is_invalid(self):
        content = self.get_request_content("mixtape")
        request = mixtapes.Session.method = Mock(autospec=True)
        request.return_value = self.mocked_response(content=content)
        mix = mixtapes.Mixtapes("some_invalid_category")
        self.assertEqual(mix._user_selected, "hot")

    def test_mixtape_initialized_with_valid_categories(self):
        content = self.get_request_content("mixtape")
        request = mixtapes.Session.method = Mock(autospec=True)
        request.return_value = self.mocked_response(content=content)

        for category in mixtapes.Mixtapes.valid_categories:
            mix = mixtapes.Mixtapes(category=category)
            self.assertEqual(mix._user_selected, category)


class TestMixtapesSearch(BaseTest, TestCase):
    def setUp(self):
        content = self.get_request_content("mixtape_search")
        method = mixtapes.Session.method = Mock(autospec=True)
        method.return_value = self.mocked_response(content=content)
        search = self.mixtape_search_parameter
        self.mix = mixtapes.Mixtapes(**search)

    def test_mixtape_validate_search_method(self):
        with self.assertRaises(MixtapesError):
            # test validate_search minimum character raise MixtapesError
            self.mix._validate_search("ab")

        with self.assertRaises(MixtapesError):
            # test validate search throw error when enter wrong datatype
            self.mix._validate_search({"hello": "world"})

        # test validate search strips whitespace
        result = self.mix._validate_search("abcd    ")
        self.assertEqual(result, "abcd")
