import re
from functools import wraps

ampersands = [
    "&quot;",
    "&amp;",
    "&lt;",
    "&gt;",
    "&nbsp;",
    "&iexcl;",
    "&cent;",
    "&pound;",
    "&curren;",
    "&yen;",
    "&brvbar;",
    "&sect;",
    "&uml;",
    "&copy;",
    "&ordf;",
    "&laquo;",
    "&not;",
    "&shy;",
    "&reg;",
    "&macr;",
    "&deg;",
    "&plusmn;",
    "&sup2",
    "&sup3;",
    "&acute;",
    "&micro;",
    "&para;",
    "&middot;",
    "&cedil;",
    "&sup1;",
    "&ordm;",
    "&raquo;",
    "&frac14;",
    "&frac12;",
    "&frac34;",
    "&iquest;",
    "&times;",
    "&divide;",
    "&ETH;",
    "&eth;",
    "&THORN;",
    "&thorn;",
    "&AElig;",
    "&aelig;",
    "&OElig;",
    "&oelig;",
    "&Aring;",
    "&Oslash;",
    "&Ccedil;",
    "&ccedil;",
    "&szlig;",
    "&Ntilde;",
    "&ntilde;",
]


class Html:
    @staticmethod
    def escape_characters(char_list):
        results = []
        if not isinstance(char_list, (list, tuple)):
            char_list = [char_list]

        for char in char_list:
            if char in ampersands:
                amps = ampersands.index(char)
                char = re.sub(amps, "", char)
            results.append(char)
        return results


class WebScrape:
    @staticmethod
    def checkRe(f):
        @wraps(f)
        def inner(obj):
            try:
                f(obj)
            except:
                raise AttributeError("re.error")
            else:
                return f(obj)

        return inner

    @staticmethod
    def get_uploader_name(string):
        """Return the name of the person whom upload the mixtape"""
        try:
            return re.search(r'.*profile/(.*\w*.*)"', string).group(1)
        except:
            return " "

    @staticmethod
    def get_uploader_bio(string):
        try:
            desc = re.findall('description"\scontent="(.*)"', string)
            if desc:
                return Html.escape_characters(desc[-1])[0].strip()
            return " "
        except:
            return " "

    @staticmethod
    def get_album_suffix_number(string):
        return re.search(r"\.(\d*)\.html", string).group(1)

    @staticmethod
    def get_embed_player_id(text):
        return re.search(r"/mixtapes/([\w\/]*)", text).group(1)

    @classmethod
    def get_song_titles(cls, text):
        songs = re.findall(r'"title"\:"(.*\w*)",\s?"artist"', text)
        songs = list(Html.escape_characters(songs))
        return songs

    @classmethod
    def get_duration_from(cls, text):
        return re.findall(r'"duration"\>(.*\d*)\<', text)

    def get_mp3_urls(text):
        return re.findall(r"fix.concat\(\s\'(.*\w*)\'", text)
