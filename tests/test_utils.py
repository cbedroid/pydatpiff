import os
from unittest.mock import Mock

PATH = os.path.dirname(os.path.abspath(__file__))


class BaseTest:

    # mixtapes and artists that are included in "mixtape" fixtures. see fixture/mixtape.html
    mixtape_list = ["A Gangsta's Pain: Reloaded", "Folarin II", "The Butterfly Effect"]
    artist_list = ["Moneybagg Yo", "Wale", "Fetty Wap"]

    # mixtape's search testing parameter
    mixtape_search_parameter = {"search": "Jay-Z"}

    def get_request_content(self, namespace="mixtape"):
        """Return testing web page content

        Raises:
            FileNotFound: test html file not found
        Returns:
            file content
        """
        file = os.path.join(PATH, "fixtures/{}.html".format(namespace))
        if not os.path.isfile(file):
            raise FileExistsError("{} test file not found".format(namespace))

        with open(file, "r") as pf:
            return pf.read()

    def mocked_response(self, status=200, content="", json=None):
        session = Mock()
        session.raise_for_status = Mock()
        session.status_code = status
        session.text = content
        session.content = content
        session.json = json or {}
        return session
