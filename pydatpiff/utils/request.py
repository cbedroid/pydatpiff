import requests
import warnings
from .helper import String
from ..errors import RequestError



class Session(object):
    '''Dynamic way to way to keep requests.Session through out whole programs.'''
    
    TIMEOUT = 10
    TIMEOUT_COUNT = 0
    def __new__(cls,*args,**kwargs):
        if not hasattr(cls,'cache'):
            cls.cache = {}
        return super(Session,cls).__new__(cls)

    def __init__(self):
        self.session = requests.Session()
        #Learn more about this 
        adapter = requests.adapters.HTTPAdapter(pool_connections=600,
                                               pool_maxsize=600)
        self.session.mount('https://', adapter)

    @classmethod
    def put_in_cache(cls,url,response):
        url = url.strip()
        cls.cache[url] = dict(count=1,response=response)
    

    @classmethod
    def clear_cache(cls):
        """ clear cache to prevent memory error"""
        del cls.cache
        cls.cache = {}


    @classmethod
    def check_cache(cls,url):
        """Checks if url already have a response.
        Stop from calling the request method more than once.
        Great for saving mobile data on mobile devices.
        """
        url = url.strip()
        try:
            if url in cls.cache.keys():
                cls.cache[url]['count'] +=1
                return cls.cache[url]['response']
        except MemoryError:
            cls.clear_cache()
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
                web = self.session.get(url,timeout=self.TIMEOUT,**kwargs)
            #POST
            if method == "post":
                web = self.session.post(url,timeout=self.TIMEOUT,**kwargs)
            #PUT
            if method == "put":
                web = self.session.put(url,timeout=self.TIMEOUT,**kwargs)
            #HEAD
            if method == "head":
                web = self.session.head(url,timeout=self.TIMEOUT)

        except requests.exceptions.InvalidURL as e:
            raise RequestError(1)

        except requests.exceptions.Timeout:
            self.TIMEOUT_COUNT +=1
            if self.TIMEOUT_COUNT >= 3:
                print('\n') # need for spacing
                warn_msg = "\nWarning:Please your internet connection ! "
                warnings.warn(warn_msg)
                self.TIMEOUT_COUNT = 0
            raise RequestError(2)

        except Exception as e:
            raise RequestError(3)
         

        status = web.status_code
        try:
            web.raise_for_status()
        except:
            raise RequestError(4)
        else:
            url = url.strip()
            self.put_in_cache(url,web)
            self.TIMEOUT_COUNT = 0
        finally:
            return web

