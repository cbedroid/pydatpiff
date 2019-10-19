import requests
from .helper import String
from .utils import Logger
from .errors import RequestError


class Session(object):
    '''Dynamic way to way to keep requests.Session through out whole programs.'''

    def __init__(self):
        self.session = requests.Session()

    def method(self, method,url,bypass=None,**kwargs):
        try:
            #GET
            if String.lower(method) == "get":
                web = self.session.get(url,timeout=10,**kwargs)
            #POST
            if String.lower(method) == "post":
                web = self.session.post(url,timeout=10,**kwargs)
            #PUT
            if String.lower(method) == "put":
                web = self.session.put(url,timeout=10,**kwargs)
            #HEAD
            if String.lower(method) == "head":
                web = self.session.head(url,timeout=10)
        except requests.exceptions.InvalidURL as e:
            raise RequestError(1)
            return 
        except Exception as e:
            raise RequestError(2)
            return 
         
        status = web.status_code
        try:
            web.raise_for_status()
        except:
            Logger.warn('Request Failed: StatusCode: %s URL: %s'%(web.status_code,url))
            raise RequestError(3)
        finally:
            return web

