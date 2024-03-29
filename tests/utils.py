import os
from functools import wraps
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock

import requests

PATH = os.path.dirname(os.path.abspath(__file__))


def tmp_wrapper(func):
    """wrapper function used to create a temporary directory and file for testing"""

    @wraps(func)
    def inner(*args, **kwargs):
        with TemporaryDirectory() as tempdir:
            with NamedTemporaryFile(dir=tempdir, delete=False) as temp_file:
                temp_file.write(b"Hello World")
                temp_file.close()
                return func(temp_file=temp_file.name, *args, **kwargs)

    return inner


class BaseTest(TestCase):
    # mixtapes and artists that are included in "mixtape" fixtures. see fixture/mixtape.html
    mixtape_list = [
        "A Gangsta's Pain: Reloaded",
        "Folarin II",
        "WEIGHT OF THE WORLD",
        "The Butterfly Effect",
        "Keys To The Streets",
        "Comethazine The Album",
        "Kawhi Leonard Presents: Culture",
        "City Lyfe Da Ep",
        "LP!",
        "Grown Man Axis",
        "Resurrected Rituals",
        "Sleep When You're Dead",
    ]

    artist_list = [
        "Moneybagg Yo",
        "Wale",
        "Maxo Kream",
        "Fetty Wap",
        "Luh Soldier & Zaytoven",
        "Comethazine",
        "Culture Jam",
        "CeOMr.stunna",
        "JPEGMAFIA",
        "Blackdice",
        "Lord Infamous",
        "J2CooL",
    ]

    # fmt: off
    # songs from MoneyBagg Yo - A Gangsta's Pain: Reloaded
    song_list = [
        "Switches  Dracs (feat. Lil Durk  EST Gee)",
        "Wat Be Wrong",
        "Gave It (feat. Big Homiie G)",
        "This Feeling (feat. Yung Bleu  Ja'niyah)",
        "Scorpio",
        "Another One (feat. DJ Khaled)",
        "Wockesha (Remix) (feat. Lil Wayne  Ashanti)",
        "Memphganistan (feat. Kaash Paige)",
        "Just Say Det",
        "GO! (feat. BIG30)",
        "Wockesha",
        "Shottas (Lala)",
        "Hard For The Next (feat. Future)",
        "If Pain Was A Person",
        "I Believe U (feat. TripStar)",
        "Time Today",
        "Interlude",
        "Free Promo (feat. Polo G  Lil Durk)",
        "Hate It Here",
        "Love It Here",
        "Clear Da Air",
        "Projects",
        "One Of Dem Nights (feat. Jhene Aiko)",
        "FR",
        "Certified Neptunes (feat. Pharrell Williams)",
        "Change Da Subject",
        "Least Ian Lie",
        "Bipolar Virgo",
        "A Gangsta's Pain",
    ]

    mixtape_links = [
        '/Moneybagg-Yo-A-Gangstas-Pain-Reloaded-mixtape.1015177.html',
        '/Wale-Folarin-II-mixtape.1015203.html',
        '/Maxo-Kream-WEIGHT-OF-THE-WORLD-mixtape.1015046.html', '/Fetty-Wap-The-Butterfly-Effect-mixtape.1015204.html',
        '/Luh-Soldier-Zaytoven-Keys-To-The-Streets-mixtape.1015180.html',
        '/Comethazine-Comethazine-The-Album-mixtape.1015179.html',
        '/Culture-Jam-Kawhi-Leonard-Presents-Culture-Jam-Vol-1-mixtape.1015178.html',
        '/CeOMrstunna-City-Lyfe-Da-Ep-mixtape.1015153.html', '/JPEGMAFIA-LP-mixtape.1015181.html',
        '/Blackdice-Grown-Man-Axis-mixtape.1015014.html', '/Lord-Infamous-Resurrected-Rituals-mixtape.1015016.html',
        '/J2CooL-Sleep-When-Youre-Dead-mixtape.1015023.html'
    ]
    # fmt: on

    # mixtape's search testing parameter
    mixtape_search_parameter = {"search": "Jay-Z"}

    @classmethod
    def get_request_content(cls, namespace="mixtape", mode="r"):
        """Return testing web page content
        :param namespace: the name of the fixture file
        :param mode: the mode of the file

        Raises:
            FileNotFound: test html file not found
        Returns:
            file content
        """
        file = os.path.join(PATH, "fixtures/{}.html".format(namespace))
        if not os.path.isfile(file):
            raise FileExistsError("{} test file not found".format(namespace))

        with open(file, mode) as pf:
            return pf.read()

    @classmethod
    def mocked_response(cls, status=200, content="", json=None, **kwargs):
        session = requests.Session = Mock(autospec=True)
        session.raise_for_status = Mock(autospec=True)
        session.status_code = status
        session.text = content
        session.content = str(content).strip().encode("utf-8")
        session.json = json or {}
        for k, v in kwargs.items():
            setattr(session, k, v)
        return session

    @classmethod
    def get_song_content(cls):
        """Return mp3 sample file path"""
        mp3_file = os.path.join(PATH, "fixtures", "test_song.mp3")
        if not os.path.isfile(mp3_file):
            raise FileExistsError("test mp3 file `{}` was not found".format(mp3_file))
        with open(mp3_file, "rb") as mp3:
            return mp3.read()
