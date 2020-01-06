import re
from functools import wraps

ampersands = [
	"&quot;", "&amp;",
	"&lt;", "&gt;",
	"&nbsp;", "&iexcl;",
	"&cent;", "&pound;",
	"&curren;", "&yen;",
	"&brvbar;", "&sect;",
	"&uml;", "&copy;",
	"&ordf;", "&laquo;",
	"&not;", "&shy;",
	"&reg;", "&macr;",
	"&deg;", "&plusmn;",
	"&sup2",
	"&sup3;", "&acute;",
	"&micro;", "&para;",
	"&middot;", "&cedil;",
	"&sup1;", "&ordm;",
	"&raquo;", "&frac14;",
	"&frac12;", "&frac34;",
	"&iquest;", "&times;",
	"&divide;", "&ETH;",
	"&eth;", "&THORN;",
	"&thorn;", "&AElig;",
	"&aelig;", "&OElig;",
	"&oelig;", "&Aring;",
	"&Oslash;", "&Ccedil;",
	"&ccedil;", "&szlig;",
	"&Ntilde;", "&ntilde;",
]

class Html:
    @staticmethod
    def checkRe(f):
        @wraps(f)
        def inner(obj):
            try:
                f(obj)
            except:
                raise AttributeError('re.error')
            else:
                return f(obj)
        return inner


    @staticmethod
    def get_end_digits(string):
        return re.search(r'\.(\d*)\.html',string).group(1)

    @staticmethod
    def toId(text):
            return re.search('/mixtapes/([\w\/]*)', text).group(1)

    @classmethod
    def find_song_names(cls,text):
        songs = re.findall(r'"title"\:"(.*\w*)",\s?"artist"',text)
        songs = list(cls.remove_ampersands(songs))
        return songs
    
    @classmethod
    def get_duration_from(cls,text):
        return  re.findall(r'"duration"\>(.*\d*)\<',text)

    @staticmethod
    def remove_ampersands(string):
        results = []
        if not isinstance(string,(list,tuple)):
            string = [string]
        for x in string:
            for amps in ampersands:
                x = re.sub(amps,'',x)
            results.append(x)
        return results
                

    def find_name_of_mp3(text):
        songs = re.findall(r'fix.concat\(\s\'(.*\w*)\'',text)
        if songs:
            return [re.sub(' ', '%20',song) for song in songs]

