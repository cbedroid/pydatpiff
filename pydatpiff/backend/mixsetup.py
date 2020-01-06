import re
from ..urls import Urls
from ..utils.request import Session
from .webhandler import Html
from .config import User,Datatype,Queued
from ..errors import MixtapesError

class Pages():
    RETRY = 5 # TODO: fix retry:: some reason parsePages fails on first try
    MAX_MIXTAPES = 520 # maximum amount of available mixtapes possible

    def __init__(self,base_response):
        self.base_response = base_response # Session.response
        self.base_url = Urls().url['base']
        self._session = Session()
        self.trys = 1

    @property
    def findPagesLinks(self):
        '''
        Return the href link from mix category or search page
        @params:: text  - the Mixtapes() _Start requests response text
            #The start up page from Mixtapes() all the page numbers
            # We grab that data and return all the page's link 
        '''
        try:
            # captures the queried response text
            XPath = re.findall(r'class\="links"(.*[\n\r]*.*\d)*</a>'
                                ,self.base_response.text)
            convert_href = [re.search('href\=.*/(.*=\d{1,2})"',x).group(1)\
                                    for x in XPath[0].split('</a>')]
        
            # map the convert_href to the base_url 
            return [''.join((self.base_url,link)) for link in convert_href]
        except: 
            # No page numbers in original url text,then return the original url
            return [self.base_response.url]


    def _Response(self,url):
        ''' This is only for Queued use only'''
        return self._session.method('GET',url).text


    def parsePages(self,re_string,bypass=False):
        '''
        Return the combine data from eachMixtapes convert_href page

        @params:: re_string - python re pattern 
        
        @@EXAMPLE
        re_string =  '<div class\="artist">(.*[.\w\s]*)</div>'
        This re_string will return all the pattern in the Mixtapes link's page text
        '''
        data = []
        re_Xpath = re.compile(re_string)
        # each page requests response data
        # Map each page links url to request.Session and 
        # place Session in 'queue and thread' 
        lrt = Queued(self._Response,self.findPagesLinks).run()
        list_response_text = Datatype.removeNone(lrt)

        #Remove all unwanted characters from Xpath 
        [data.extend(list(Html.remove_ampersands(pat.group(1))[0]\
                        for pat in re_Xpath.finditer(RT)\
                        if pat is not None))
                        for RT in list_response_text]

        # hackable way to fix this function from not return data on first try
        # recalling the function if its returns None 
        if not data:
            if self.trys < self.RETRY:
                self.trys+=1
                return self.parsePages(re_string)
            else:
                raise MixtapesError(3)
        elif len(data) < self.MAX_MIXTAPES and not bypass:
            # Try to get the maximun amount of mixtapes
            # Since the first time this function is called, the data weirdly return None
            # We keep trying until we get the max amount of mixtapes

            if self.trys < self.RETRY:
                self.trys+=1
                return self.parsePages(re_string)
            else:
                #print('Fuck it')
                return self.parsePages(re_string,True)

        return data

