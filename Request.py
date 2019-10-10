import requests
import json 
import logging
import user_agent as ua
from functools import wraps
from helper import String

class RequestError(Exception):
  pass


class Session(object):
  ''' Dynamic way to way to keep the requests.Session 
      through out whole programs
  '''
  def __new__(cls,*args,**kwargs):
    log_level = kwargs.get('level',logging.WARNING)
    #logging.basicConfig(level=log_level)

    if not hasattr(cls,'_session'):
      cls._session = requests.Session()
      cls._user_agent = ua.generate_user_agent()
      cls._logger =  logging.getLogger(__name__)
      cls._logger.setLevel(log_level)
      handler = logging.FileHandler('logs.log')
      formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
      handler.setFormatter(formatter)
      cls._logger.addHandler(handler)

      cls._token_jar = requests.cookies.RequestsCookieJar()
      cls._headers =cls._session.headers

      cls._session.headers.update(**cls._headers) 
      return super(Session,cls).__new__(cls)
  
  def __init__(self,*args,**kwargs):
      super(Session,self).__init__(*args,**kwargs)

  @property
  def logger(self):
      return self._logger
 
  @property
  def token_jar(self):
    ''' Token_Jar - RequestsCookieJar that store all of the response headers and cookie 
        tokens. These token will be passed to other request headers
    '''
    return self._token_jar

  @token_jar.setter
  def token_jar(self,token):
    #TODO:FIX THIS - token not setting using = , only update 
    try:
      self._token_jar.update(**token)
    except:
      self.logger.warning('Token not set properly: %s'%token) 

  def _get_token(self,tokenname):
    ''' return token_jar item. if None, raise Attribute Error
    '''
    token = self.token_jar.get(tokenname)
    if token:
      return token
    '''
    msg = 'Token Error: Token "%s" was not found'%tokenname
    self.logger.critical('%s. Program halted'%msg)
    raise RequestError(msg)
    '''

  @classmethod
  def _persistence(self):
    return self._session
 
  @property
  def session(self):
      return self._session

  def responder(f):
      '''For logging purpose: 
        Capture all the requests responses and save them to variable
        "status" for future analyses
      ''' 
      @wraps(f)
      def inner(self,*args,**kwargs):
        if not hasattr(self,'_responses') or not hasattr(self,'_order') :
          self._responses = {}
          self._order = 0
        name = f.__name__
        response = f(self,*args,**kwargs)
        try:
          resp_url = response.url
          status = response.status_code
        except:
          # catching status code error
          resp_url = 'UNKNOWN' #response.url
          status = 'FAILED'
        try:
          if name in self._responses.keys():
            # Function that are called repeatly,increment the name 
            name+='_2'
          self._responses[name] = {'response':response,'order':self._order,'url':resp_url}
          self._order+=1

          # capture token from response  
          if response:
            self.token_jar.update(response.cookies)
        except:
          msg = 'Invalid requests response from url: %s'%resp_url
          raise RequestError(msg)

        return response
      return inner

  @property
  def status(self):
    if not hasattr(self,'_responses'):
      return None
    return [stats for stats in sorted(self._responses.items(),key=lambda x: x[1].get('order'))]


  @property
  def headers(self):
    return self._headers

  @headers.setter
  def headers(self,kw):
    '''Update the requests session headers '''
    print('\nSetting Headers')
    # Note: any headers pass here will be persistence


  def method(self, method,url,bypass=None,**kwargs):

    #This head request must be called each time a requst to pandora api 
    headers = kwargs.pop('headers',{})
    headers.update(**self.headers)

    try:
      #GET
      if String.lower(method) == "get":
        web = self.session.get(url,**kwargs,cookies=self.session.cookies,timeout=10)
      #POST
      if String.lower(method) == "post":
        web = self.session.post(url,**kwargs,cookies=self.session.cookies,timeout=10)
      #PUT
      if String.lower(method) == "put":
        web = self.session.put(url,**kwargs,cookies=self.session.cookies,timeout=10)
      #HEAD
      if String.lower(method) == "head":
        web = self.session.head(url,cookies=self.session.cookies,timeout=10)

    except requests.exceptions.InvalidURL as e:
      self.logger.warning('\nUrl: "%s" is missing some characters'%(url))
      return
    except Exception as e:
      self.logger.warning('Something went wrong %s\n'%url)
      return 
     
    status = web.status_code
    # let some status code through although they are bad 
    if bypass:
      if any(str(webcode) == status for webcode in bypass):
        return web
    else:
      try:
        web.raise_for_status()
      except:
          self.logger.warning('Request Failed: StatusCode: %s URL: %s'%(web.status_code,url))
          return web 
      else:
        self.logger.info('requests passed %s'%web)    
    return web


