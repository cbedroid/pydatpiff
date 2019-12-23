import re
from ..urls import Urls
from ..utils.request import Session
from .webhandler import Html

class Pages():

    def __init__(self,base_text):
        self.base_text = base_text # captures the queried response text
        self.base_url = Urls().url['base']
        self._session = Session()

    @property
    def getPageLinks(self):
        '''
        Return the href link from mix category or search page
        @params:: text  - the Mixtapes() _Start requests response text
            #The start up page from Mixtapes() all the page numbers
            # We grab that data and return all the page's link 
        '''
        path = re.findall(r'class\="links"(.*[\n\r]*.*\d)*</a>'
                            ,self.base_text)
        links = [re.search('href\=.*/(.*=\d{1,2})"',x).group(1)\
                                for x in path[0].split('</a>')]
        
        # map the links to the base_url 
        return [''.join((self.base_url,link)) for link in links]
    


    def getReData(self,re_string):
        '''
        Return the combine data from eachMixtapes links page

        @params:: re_string - python re pattern 
        
        @@EXAMPLE
        re_string =  '<div class\="artist">(.*[.\w\s]*)</div>'
        This re_string will return all the pattern in the Mixtapes link's page text
        '''
        data = []
        pattern = re.compile(re_string)
        # each page requests response data
        pages_text = [self._session.method('GET',links).text\
                            for links in self.getPageLinks]


        [data.extend(list(Html.remove_ampersands(pat.group(1))[0]\
                        for pat in pattern.finditer(pt)\
                        if pat is not None))
                        for pt in pages_text]
        return data



