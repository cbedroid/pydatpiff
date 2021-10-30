import os
from unittest.mock import Mock

PATH = os.path.dirname(os.path.abspath(__file__))


class BaseTest:
    # mixtapes and artists that are included in "mixtape" fixtures. see fixture/mixtape.html
    mixtape_list = ["A Gangsta's Pain: Reloaded", "Folarin II", "The Butterfly Effect"]
    artist_list = ["Moneybagg Yo", "Wale", "Fetty Wap"]

    # fmt: off
    # songs from MoneyBagg Yo - A Gangsta's Pain: Reloaded
    song_list = [
        "Switches  Dracs (feat. Lil Durk  EST Gee)", "Wat Be Wrong", "Gave It (feat. Big Homiie G)",
        "This Feeling (feat. Yung Bleu  Ja'niyah)", "Scorpio", "Another One (feat. DJ Khaled)",
        "Wockesha (Remix) (feat. Lil Wayne  Ashanti)", "Memphganistan (feat. Kaash Paige)", "Just Say Det",
        "GO! (feat. BIG30)", "Wockesha", "Shottas (Lala)",
        "Hard For The Next (feat. Future)", "If Pain Was A Person", "I Believe U (feat. TripStar)",
        "Time Today", "Interlude", "Free Promo (feat. Polo G  Lil Durk)",
        "Hate It Here", "Love It Here", "Clear Da Air",
        "Projects", "One Of Dem Nights (feat. Jhene Aiko)", "FR",
        "Certified Neptunes (feat. Pharrell Williams)",
        "Change Da Subject", "Least Ian Lie", "Bipolar Virgo",
        "A Gangsta's Pain",
    ]
    # fmt: on

    # mixtape's search testing parameter
    mixtape_search_parameter = {"search": "Jay-Z"}

    def get_request_content(self, namespace="mixtape", mode="r"):
        """Return testing web page content

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

    def mocked_response(self, status=200, content="", json=None, **kwargs):
        session = Mock()
        session.raise_for_status = Mock()
        session.status_code = status
        session.text = content
        session.content = str(content).strip().encode("utf-8")
        session.json = json or {}
        for k, v in kwargs.items():
            setattr(session, k, v)
        return session
