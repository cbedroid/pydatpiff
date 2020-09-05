import os
import sys
import unittest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from ..test_utils import mockSessionResponse, Fake_Session_Mock
from ... import mixtapes

# from .. import pydatpiff


dp_real_link = "https://mobile.datpiff.com/mixtape/983402?trackid=1&platform=desktop"
dummy_text = "<blah blah blah>"
dummy_json_data = {"success": True, "data": "foo-bar"}

mocked_session = mockSessionResponse(
    status=200, text=dummy_text, json_data=dummy_json_data
)


# class Test_Mixtapes(unittest.TestCase):
#   class TestSession(mixtapes.Session):
#     session = mocked_session
#     TIMEOUT = 10
#     cache = {}

#     @classmethod
#     def put_in_cache(cls,*args,**kwargs):
#       return {}

#     @classmethod
#     def clear_cache(cls):
#       cls.cache = {}

#     def method(self,*args,**kwargs):
#       return mocked_session

#   class TestMix(mixtapes.Mixtapes):
#     _session = mocked_session

#   #mixtapes.Session = mocked_session
#   #session = mixtapes.Session
#   #SESSSION = mixtapes.Session
#   def setUp(self):
#     self.SESSION = patch.object(mixtapes,"Session",autospec=mixtapes.Session).start()
#     #self.mix = patch.object(mixtapes,'Mixtapes').start()
#     self.addCleanup(patch.stopall)

#   # def test_mixtapes_session_is_mocked_session(self):
#   #   self.mix._session = mocked_session
#   #   real_mix = Mixtapes()
#   #   self.assertEqual(self.mix._session,mocked_session)

#   def test_mixtapes_search_with_wrong_parameter_return_mixtapes(self):
#     # break the search function and check if Mixtapes
#     # return default category mixtapes

#     # break search by NOT specifying a search
#     start = mixtapes.Mixtapes(search=None)
#     count = start.call_count
#     self.assertEqual(count,1)
