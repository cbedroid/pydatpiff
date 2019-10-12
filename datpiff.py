__author__ = 'Cornelius Brooks'
__date__ = 'Feb 3, 2019'
__description__ =''' Datpiff music player that lets user control,download, and play  music from cmdline  '''
__version__ = 'V0.0.1'
import os
import sys
import re
import platform
import subprocess as sp
import threading
import platform
from colorama import Fore
import atexit
from functools import wraps
from time import sleep
from string import punctuation as strp
from bs4 import BeautifulSoup 
from builtins import print as _print
#from media import Media
from .Request import Session


class DatpiffError(Exception):
    pass

class Verbose(object):
    def __init__(self,verbose = True):
        self.verbose = verbose

    def print(self,*msg):
        if self.verbose:
            _print(*msg)
print = Verbose().print

class Mixtapes(Session):
    def __new__(cls, *args, **kwargs):
 
        cls.category = {"hot":"http://www.datpiff.com/mixtapes/hot",
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
        cls.soup =None
        return super(Mixtapes, cls).__new__(cls)


    def __init__(self, category=None, show_help=True,*args,**kwargs):
        ''' takes one arguement:
            category:  -- see Mixtapes.category
        '''
        super(Mixtapes,self).__init__(*args,**kwargs)
        self.main_url = "http://www.datpiff.com"
        page = self.category.get(category) or self.category['hot']
        self.Start(page)
        self.show_help = show_help
        self._setup()
        self._trys = 1 # use to catch user errors

    def __str__(self):
        category = "'new','hot','top','celebrated'"
        return "%s(category)  argument: category --> %s"%(self.__class__.__name__, category)


    def __repr__(self):
        return "%s('hot')"%self.__class__.__name__

    @Session.responder
    def Start(self, url_page):
        ''' Start the web page from category selected\n--see Mixtapes.__init__'''
        # return the url page request by user
        body = self.method('GET',url_page)
        return body


    def soupPaths(self,soups=None):
        ''' Function use to find all of the links pages inside BeautifulSoup.
            data will be add on to the data of the original pages 
            pages1,pages2..etc -> collect data and append it to -> (first request page)
        '''
        original = BeautifulSoup(self._responses['Start']['response'].content,'html5lib')
        if orginal:
            try:
                path = original.find('div',class_='pagination').div
                href = path.findall('a',href=True)
                if href:
                    for links in href:
                        try:
                            yield ''.join((self.main_url,links.a.get('href')))
                        except:
                            pass
            except Exception as e:
                print(e)

    def _checkSize(self,obj):
        '''break down list object to find the most accurate choice'''
        if not isinstance(obj,list):
            return "".join(obj)
        raw_obj = obj
        total = len(obj)
        if total > 1:
            if self._trys > 3:
                print(Fore.YELLOW + '\nToo many trys..Selecting default artist'+
                        Fore.RESET)
                self._trys = 0
                self._checkSize(1)
            else:
                msg = "\nMAKE A SELECTION:"
                print(Fore.GREEN + "%s"%(msg))
                print(Fore.RESET + '-'*len(msg))
                [print("%s) %s"%(c+1,x)) for c,x in enumerate(raw_obj)] 
                choice = input("\nselect >> ")
                if not choice:
                    self._trys += 1
                    self._checkSize(obj)

            print('CHOICE: ',choice)
            if choice.isdigit() or choice.isnumeric():
                # number is entered
                print('checking by number')
                choice = int(choice) -1
                if choice > total:
                    choice = total
                else:
                    obj = "".join(raw_obj[int(choice)])
            else:
                # checking for word comparison
                print("\nChecking by words")
                choice = choice.lower().strip()
                if any([ choice in _list.lower().strip() for _list in raw_obj]):
                    obj = [x for x in raw_obj \
                        if choice in x.lower().strip()]
                    if len(obj) >1: # Rechecking size
                        print(Fore.RED + "Too many selection.",
                            Fore.YELLOW +"\nYou should choose by number"+ Fore.RESET)
                        obj=Mixtapes._checkSize(raw_obj)
                    else:
                        obj = "".join(obj)
        else:
            obj= "".join(raw_obj)
        return obj


    @classmethod
    def _category(cls):
        print("\n--- URL CATEGORY ---")
        for key, val in cls.page.items():
            print("%s" % (key))


    def _searchTree(f):
        '''Decorator function 
           Search through the category set page and returns the child function
             and set a private attrib of the child function.
              example: "function()" will attribute "_function"
            params: (child function params) 
            return examples:: artist name,title,album ...etc
        '''

        @wraps(f) 
        def inner(self, *args,**kwargs):
            response_text  = self._responses['Start']['response'].text
            name = f.__name__
            path = f(self,*args,**kwargs)
            pattern = re.compile(path)
            data = list( pat.group(1) for pat in pattern.finditer(response_text) )

            if hasattr(self,'_artists'):
                data = data[:len(self._artists)]
            dunder = '_'+name
            setattr(self,dunder,data)
            return data
        return inner


    def _setup(self):
        self.artists = '<div class\="artist">([.\w\s]*)</div>'
        self.titles  = 'title\="listen to[.\w\s"]*>([.\w\s]*)</a>'
        self.links   = 'title"><a href\=\"(.*[\w\s]*\.html)"'
        self.views   = '<div class\="text">Listens: <span>([\d,]*)</span>'

    @property
    def artists(self):
        ''' return all albums artist name from web page'''
        if hasattr(self,'_artists'):
            return self._artists

    @artists.setter
    @_searchTree
    def artists(self,path):
        return path


    @property
    def titles(self):
        if hasattr(self,'_titles'):
            return self._titles

    @titles.setter 
    @_searchTree
    def titles(self,path):
        ''' return all the album titles from web page'''
        return path

    @property
    def links(self):
        if hasattr(self,'_links'):
            return self._links

    @links.setter
    @_searchTree
    def links(self,path):
        ''' return all the album links from web page'''
        return path
    

    @property
    def views(self):
        if hasattr(self,'_views'):
            return self._views

    @views.setter
    @_searchTree
    def views(self,path):
        ''' return all the album views count from web page'''
        return path

    @property
    def display(self):
        ''' Prettify all albums information  
            and display it to screen 
        '''
        links = self._links
        data = zip(self._artists, self._titles, links, self._views)
        for count,(a, t, l, v) in list(enumerate(data,start=1)):
            print("# %s\nArtist: %s\nAlbum: %s\nLinks: %s\nViews: %s\n%s"
                    % (count, a, t, l[1:], v, "-"*40))


    def _select(self,selection):
        ''' select ablums_link by artist name, album name ('title')
         or by index number of title or artist
        '''
        try:
            link = list(self._links)
            artist = [x.lower().strip() for x in self._artists]
            title = [x.lower().strip() for x in self._titles]
            every = [x for x in artist] + [x for x in title]

            if isinstance(selection, (int)):
                length = len(title)
                if int(selection) > length:
                    selection = length
                    return link[selection-1], selection-1
                elif selection == 0:
                    return link[selection], selection
                else:
                    return link[selection-1], selection-1
            else:
                selection = selection.strip().lower()


            if any([selection in t for t in title]):
                # Get link by title name
                selection = "".join([t for t in title if selection.strip() in t])
                selection = self._checkSize(selection)
                selector = title.index(selection)
                print("getting by Title")
                print("%s) link: %s" % (selector, link[selector]))
                return link[selector], selector

            elif any([selection in a for a in artist]):
                # Get link by artist name
                selection = [ a for a in artist if selection.strip() in a]
                selection = self._checkSize(selection)
                 
                selector = artist.index(selection)
                print("getting by Artist")
                print("selector:", selector)
                print("%s) link: %s" % (selector, link[selector]))
                return link[selector], selector
            else:
                
                return None
        except DatpiffError as e:
            print(Fore.RED + "Error No Album Selected" + Fore.RESET)
            print(e)



if __name__ == "__main__":
    from importlib import reload as rl 
    from .media import Media as md
    mix = Mixtapes("hot")
    media = md(mix)
    text = mix._responses['Start']['response'].text
    
