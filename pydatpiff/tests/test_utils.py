import os 
import sys 
from unittest.mock import Mock,patch
from ..mixtapes import Mixtapes 
from ..media  import Media


def run_mix(category='hot',search=None):
    if search:
        return Mixtapes(search=search)
    else:
        return Mixtapes(category)

def run_media():
    return Media(Mixtapes())


def mockSessionResponse(status=200,text="content here",
                                json_data=None,raise_for_status=None):
        response = Mock()
        response.raise_for_status = Mock()
        response.status_code = status
        response.text = text
        response.json = Mock()
        response.json.return_value = json_data or {}

        if raise_for_status:
            response.status_code.side_effect = raise_for_status

        return response

