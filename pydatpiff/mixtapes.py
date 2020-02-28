import re
from functools import wraps
from .urls import Urls
from .utils.request import Session
from .errors import MixtapesError
from .frontend.display import Print,Verbose
from .backend.config import User,Datatype
from .backend.mixsetup import Pages


class Mixtapes(object):
    category = list(Urls.category)

    def __new__(cls, *args, **kwargs):
        return super(Mixtapes, cls).__new__(cls)


    def __init__(self, category=None,search=None,*args,**kwargs):
        """
        Mixtapes Initialization.

        :param: category - name of the catgeory to search from.
                            see Mixtapes.category

        :param: search - search for an artist or mixtape's name
        """
        super(Mixtapes,self).__init__(*args,**kwargs)
        self._session = Session()
        self._session.clear_cache()
        self._Start(category,search)
        self._setup()


    def __str__(self):
        category = "'new','hot','top','celebrated'"
        return "%s(category)  argument: category --> %s"%(self.__class__.__name__, category)


    def __repr__(self):
        return "%s('hot')"%self.__class__.__name__


    def __len__(self):
        if hasattr(self,'_artists'):
            return len(self._artists)
        else:
            return 0


    def search(self,name):
        """
        Search for an artist or mixtape's name.

        :param: name - name of an artist or mixtapes name 
        """
        name = str(name).strip()
        if not name: 
            return 

        Verbose('\nSearching for %s mixtapes ...'%name.title())
        url = Urls.url['search']
        return  self._session.method('POST',url,data=Urls.payload(name))


    def _Start(self,category='hot', search=None):
        """
        Initial setup. Gets all available mixtapes.
        
        :param: category - name of the catgeory to search from.
                            (self Mixtapes.category)
        :param: search - search for an artist or mixtape's name
        """
        if search: # Search for an artist 
            body = self.search(search)
            if not body or body is None: # on failure return response from a category 
                return self._Start('hot')
        else: # Select from category instead of searching 
            select = User.choice_is_str
            choice = select(category,Urls.category) or select('hot',Urls.category)
            body = self._session.method('GET',choice)
        self._responses = body
        return body

   
    def _setup(self):
        """Initial class variable and set theirattributes on page load up.
        """
        # all method below are property setter method 
        # each "re string" get pass to the corresponding html response text

        self.artists = '<div class\="artist">(.*[.\w\s]*)</div>'
        self.mixtapes  = '"\stitle\="listen to ([^"]*)">[\r\n\t\s]?.*img'
        self.links   = 'title"><a href\=\"(.*[\w\s]*\.html)"'
        self.views   = '<div class\="text">Listens: <span>([\d,]*)</span>'
        Verbose('Found %s Mixtapes'%len(self))


    def _searchTree(f):
        """
        Wrapper function that parse and filter all requests response content.
        After parsing and filtering the responses text, it then creates a 
        dunder variable from the parent function name. 
        
        :param: f  (wrapper function) 
         #----------------------------------------------------------
         example: "function()" will create an attribute "_function"
         #----------------------------------------------------------
        """
        @wraps(f) 
        def inner(self, *args,**kwargs):
            name = f.__name__
            path = f(self,*args,**kwargs)
            pattern = re.compile(path)
            data = Pages(self._responses).getRePattern(pattern)
            if hasattr(self,'_artists'):
                # we map all attributes length to _artists length 
                data = data[:len(self._artists)]
            dunder = '_' + name
            setattr(self,dunder,data)
            return data
        return inner


    @property
    def artists(self):
        """ return all Mixtapes artists' name"""
        if hasattr(self,'_artists'):
            return self._artists

    @artists.setter
    @_searchTree
    def artists(self,path):
        return path


    @property
    def mixtapes(self):
        """ Return all mixtapes name""" 
        if hasattr(self,'_mixtapes'):
            return self._mixtapes

    @mixtapes.setter 
    @_searchTree
    def mixtapes(self,path):
        ''' return all the mixtapes titles from web page'''
        return path


    @property
    def links(self):
        """Return all of the Mixtapes' url links"""
        if hasattr(self,'_links'):
            return self._links

    @links.setter
    @_searchTree
    def links(self,path):
        return path
    

    @property
    def views(self):
        """Return the views count of each mixtapes"""
        if hasattr(self,'_views'):
            return self._views

    @views.setter
    @_searchTree
    def views(self,path):
        return path


    def display(self):
        """ Prettify all Mixtapes information and display it to screen 
        """
        links = self._links
        data = zip(self._artists, self._mixtapes, links, self._views)
        for count,(a, t, l, v) in list(enumerate(data,start=1)):
            Print("# %s\nArtist: %s\nAlbum: %s\nLinks: %s\nViews: %s\n%s\n"
                    % (count, a, t, 'https://datpiff.com'+l, v, "-"*60))


    def _select(self,select):
        """
        Queue and load  a mixtape to media player.
                            (See pydatpiff.media.Media.setMedia)
        
        :param: select - (int) user selection by indexing an artist name or album name
                            (str)
        """
        try:
            # Return the user select by either integer or str
            # we map the integer to artists and str to mixtapes 
            return User.selection(select,self.artists,self.mixtapes)

        except MixtapesError as e:
            Print(e)
            raise MixtapesError(1)

