import os
import re
import sys
from unittest.mock import Mock, MagicMock, PropertyMock, patch
from ..mixtapes import Mixtapes
from ..media import Media
from ..utils import request


def run_mix(category="hot", search=None):
    if search:
        return Mixtapes(search=search)
    else:
        return Mixtapes(category)


def run_media():
    return Media(Mixtapes())


def mockSessionResponse(
    status=200, text="content here", json=None, raise_for_status=None, *args, **kwargs
):
    response = MagicMock()
    response.raise_for_status = Mock()
    response.status_code = status
    response.text = text
    response.content = Mock(return_value=kwargs.get("content", text))
    response.json = Mock(return_value=json or kwargs.get("json_data", {}))
    response.url = Mock(return_value=kwargs.get("url", ""))

    response.method = Mock(*args, **kwargs, return_value=response)
    response.method.text = text
    response.method.content = Mock(return_value=text)
    response.clear_cache = Mock(return_value="cleared")

    if raise_for_status:
        response.status_code.side_effect = raise_for_status

    return response


# Here we will create a dummy testing Regex using some bultin Regex functionality.
# Builtin Regex WILL NOT be overwritten
def mockRegex(
    string="hello world",
    array=[],
    throw_exception=False,
    exception_type=AttributeError,
    *args,
    **kwargs
):
    data = Mock()
    data.sub = Mock(*args, return_value=string)

    if throw_exception:
        data.search = Mock(*args, side_effect=exception_type)
        data.findall = Mock(*args, side_effect=exception_type)
        data.search.group = Mock(*args, side_effect=exception_type)
    else:
        data.search = Mock(args, return_value=string)
        data.search.group = *args, Mock(return_value=string)
        data.findall = Mock(*args, return_value=list(*array))
    return data


@patch.object(request, "Session", autospec=True)
class Fake_Session_Mock:
    TIMEOUT = 10
    TIMEOUT_COUNT = 0
    cache = {}

    def __init___(self):
        self.session = mocked_session

    @classmethod
    def put_in_cache(cls, *args, **kwargs):
        pass

    @classmethod
    def clear_cache(cls):
        cls.cache = {}

    @classmethod
    def method(cls, *args, **kwargs):
        return mockSessionResponse()
