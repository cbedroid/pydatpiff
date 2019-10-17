__author__ = 'Cornelius Brooks'
__date__ = 'Feb 3, 2019'
__description__ =''' Datpiff music player that lets user control,download, and play  music from cmdline  '''
__version__ = 'V1.0.1'

import os
import re
from functools import wraps
from builtins import print as _print
from .Request import Session
import requests


class DatpiffError(Exception):
    pass

class Verbose(object):
    def __init__(self,verbose = True):
        self.verbose = verbose

    def print(self,*msg):
        if self.verbose:
            _print(*msg)
print = Verbose().print


class Mixtapes(object):
    def __new__(cls, *args, **kwargs):
 
        cls._category = {"hot":"http://www.datpiff.com/mixtapes/hot",
                        "new":"http://www.datpiff.com/mixtapes",
                        "top":"http://www.datpiff.com/mixtapes-top",
                        "celebrated":"http://www.datpiff.com/mixtapes/celebrated",
                        "popular":"http://www.datpiff.com/mixtapes-popular.php",
                        "exclusive":"http://www.datpiff.com/mixtapes-exclusive",
                        "most download":"http://www.datpiff.com/mixtapes-popular.php?sort=downloads",
                        "most listen":"http://www.datpiff.com/mixtapes-popular.php?filter=month&sort=listens",
                        "most favorite":"http://www.datpiff.com/mixtapes-popular.php?sort=favorites",
                        "highest rating":"http://www.datpiff.com/mixtapes-popular.php?filter=month&sort=rating"
                    }
        return super(Mixtapes, cls).__new__(cls)


    def __init__(self, category=None,search=None,*args,**kwargs):
        '''
        Mixtapes Initialize 
        @@params: category:  -- see Mixtapes.category
        '''
        super(Mixtapes,self).__init__(*args,**kwargs)
        self._session = requests.Session()
        self.main_url = "http://www.datpiff.com"
        page = self._selectCategory(category)  or self._category['hot']
        self._Start(page,search)
        self._setup()

    def __str__(self):
        category = "'new','hot','top','celebrated'"
        return "%s(category)  argument: category --> %s"%(self.__class__.__name__, category)


    def __repr__(self):
        return "%s('hot')"%self.__class__.__name__


    def search(self,artist):
        """search for an artist mixtapes."""
        try:
            print('\nSearching for %s mixtapes ..'%artist)
            url = 'https://www.datpiff.com/mixtapes-search'
            data = {'submit':'MTAxNTUuNzcxNTI5NDEyMzY0MTgwNzEx','criteria':artist}
            web = requests.post(url,data=data,timeout=10)
            web.raise_for_status()
        except:
            print('Error searching for %s mixtape'%artist)
        else:
            return web


    def _selectCategory(self,index):
        """Helper function for selecting a category on startup
        @@params: index - category to search for. 
                (See --> "Mixtapes.category" for all category)
        """
        choosen = list(filter(lambda x: str(index) in x,self._category))
        if choosen:
            return min(choosen)


    def _setup(self):
        """Initial variable and set attributes on page load up."""
        self.artists = '<div class\="artist">(.*[.\w\s]*)</div>'
        self.mixtapes  = '"\stitle\="listen to ([^"]*)">[\r\n\t\s]?.*img'
        #[.\w\s\&]*)[^">]'
        #(.*[\w\s]*)'
        self.links   = 'title"><a href\=\"(.*[\w\s]*\.html)"'
        self.views   = '<div class\="text">Listens: <span>([\d,]*)</span>'



    def _Start(self, url_page,search=None):
        '''
        Starts the web page from category selected by user
        (see Mixtapes.__init__)
        '''
        # return the url page request by user
        if search:
            body = self.search(search)
            if not body.text: # if the search requests fails then get default page 
                print('search Failed')
                # discard search then we recalls the _Start 
                return self._Start(url_page,None)
        else:
            if not url_page: 
                # although it should be set. we check again incase of user mistake
                url_page = self._category['hot']
            body = self._session.get(url_page)
        self._responses = body
        return body


    @property
    def category(self):
        """All category of Mixtapes that users can choose from."""
        print("\n--- URL CATEGORY ---")
        for key, val in self._category.items():
            print("%s" % (key))


    def _searchTree(f):
        '''
        Wrapper function that parse and filter all requests response content.
        After parsing and filtering the responses text, it then creates a 
        dunder variable from the parent function name. 
        
        params: (wrapper function) 
         #----------------------------------------------------------
         example: "function()" will create an attribute "_function"
         #----------------------------------------------------------
        '''
        @wraps(f) 
        def inner(self, *args,**kwargs):
            response_text  = self._responses.text
            name = f.__name__
            path = f(self,*args,**kwargs)
            pattern = re.compile(path)
            data = list( re.sub('amp;','',pat.group(1))\
                    for pat in pattern.finditer(response_text)\
                    if pat is not None)

            if hasattr(self,'_artists'):
                data = data[:len(self._artists)]
            dunder = '_'+name
            setattr(self,dunder,data)
            return data
        return inner


    @property
    def artists(self):
        ''' return all Mixtapes artists name'''
        if hasattr(self,'_artists'):
            return self._artists

    @artists.setter
    @_searchTree
    def artists(self,path):
        return path


    @property
    def mixtapes(self):
        if hasattr(self,'_mixtapes'):
            return self._mixtapes

    @mixtapes.setter 
    @_searchTree
    def mixtapes(self,path):
        ''' return all the mixtapes titles from web page'''
        return path

    @property
    def links(self):
        """Return all of the Mixtapes url links"""
        if hasattr(self,'_links'):
            return self._links

    @links.setter
    @_searchTree
    def links(self,path):
        ''' return all the album links from web page'''
        return path
    

    @property
    def views(self):
        """Return the view count of each mixtapes"""
        if hasattr(self,'_views'):
            return self._views

    @views.setter
    @_searchTree
    def views(self,path):
        return path

    @property
    def display(self):
        ''' Prettify all Mixtapes information  
            and display it to screen 
        '''
        links = self._links
        data = zip(self._artists, self._mixtapes, links, self._views)
        for count,(a, t, l, v) in list(enumerate(data,start=1)):
            print("# %s\nArtist: %s\nAlbum: %s\nLinks: %s\nViews: %s\n%s"
                    % (count, a, t, l[1:], v, "-"*40))


    def _select(self,select):
        ''' select ablums_link by artist name, album name ('title')
         or by index number of title or artist
        '''
        try:
            combine = list(zip(self.artists,self.mixtapes))
            select = 1 if select == 0 else select
            mixtapes  = dict(enumerate(combine,start=1))
            choice = list(filter(lambda x: select in x \
                            or str(select).lower().strip() in x[1][0].lower()
                            or str(select).lower().strip() in x[1][1].lower(),
                            (mixtapes.items())
                             ))
            if choice:
                index = (min(choice)[0]) - 1
                return self._links[index],index
            else:
                print('\n\t -- No Mixtape was found --')
                return 
        except DatpiffError as e:
            print("Error No Album Selected")
            print(e)

