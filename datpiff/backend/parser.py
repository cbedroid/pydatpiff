import re
from functools import wraps

class Reparse:

    @staticmethod
    def checkRe(f):
        @wrap(f)
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
    def to_songs(cls,text):
        songs = re.findall(r'"title"\:"(.*\w*)",\s?"artist"',text)
        songs = cls.removeAmp(songs)
        return songs
    
    @classmethod
    def duration(cls,text):
        return  re.findall(r'"duration"\>(.*\d*)\<',text)

    @staticmethod
    def removeAmp(string):
        if not isinstance(string,(list,tuple)):
            string = [string]
        return [re.sub(r'amp;', '', x) for x in string]

    
    @staticmethod
    def encodeMp3(text):
        songs = re.findall(r'fix.concat\(\s\'(.*\w*)\'',text)
        if songs:
            return [re.sub(' ', '%20',song) for song in songs]

