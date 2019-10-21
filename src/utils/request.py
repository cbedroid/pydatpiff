import requests
from .helper import String
from src.logger import Logger
from src.errors import RequestError


class Session(object):
    '''Dynamic way to way to keep requests.Session through out whole programs.'''
    def __new__(cls,*args,**kwargs):
        if not hasattr(cls,'cache'):
            cls.cache = {}
        return super(Session,cls).__new__(cls)

    def __init__(self):
        self.session = requests.Session()

    def put_in_cache(self,url,response):
        url = url.strip()
        self.cache[url] = dict(count=1,response=response)

    def check_cache(self,url):
        """Checks if url already have an response.
        Stop from calling the request method more than once.
        Great for saving mobile data on mobile devices.
        """
        url = url.strip()
        try:
            if url in self.cache.keys():
                self.cache[url]['count'] +=1
                return self.cache[url]['response']
        except:
            pass 
            
    def method(self, method,url,bypass=None,**kwargs):
        """ urllib requests method """
        method = String.lower(method)
        cache = self.check_cache(url) 
        if cache and method != 'post':
            return cache

        try:
            #GET
            if method == "get":
                web = self.session.get(url,timeout=10,**kwargs)
            #POST
            if method == "post":
                web = self.session.post(url,timeout=10,**kwargs)
            #PUT
            if method == "put":
                web = self.session.put(url,timeout=10,**kwargs)
            #HEAD
            if method == "head":
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
        else:
            url = url.strip()
            self.put_in_cache(url,web)
        finally:
            return web

