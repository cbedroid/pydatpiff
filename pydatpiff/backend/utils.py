"""
    This file will stored all dynamic class and methods.
    These methods will be used throughout the whole program.

"""
import concurrent.futures as cf
import sys  # noqa: F401
import threading
from functools import wraps


class ThreadPool:
    pool = []


def Threader(f):
    @wraps(f)
    def inner(*a, **kw):
        t = threading.Thread(target=f, args=(a), kwargs=dict(kw))
        t.daemon = True
        t.start()
        return t

    return inner


class ThreadQueue:
    def __init__(self, main_job, input_work, *args, **kwargs):
        self.input = input_work  # work to put in queue
        self.main_job = main_job  # job to perform with work

    def execute(self, *args, **kwargs):

        with cf.ThreadPoolExecutor() as ex:
            if args or kwargs:
                args = tuple(args) * len(self.input)
                kwargs = list(dict(kwargs) for _ in range(len(self.input)))
                data = ex.map(self.main_job, self.input, args, kwargs)
            else:
                data = ex.map(self.main_job, self.input)
        return [x for x in data]


class Object:
    @staticmethod
    def isDict(_type):
        return isinstance(_type, dict)

    @staticmethod
    def isStr(_type):
        return isinstance(_type, str)

    @staticmethod
    def isList(_type):
        return isinstance(_type, list)

    @classmethod
    def removeNone(cls, _list):
        return list(filter(None, _list))

    @classmethod
    def enumerate_it(cls, data, start=0):
        """Return enumerate object"""
        if cls.isDict(data) or cls.isList(data):
            if cls.isDict(data):
                data = data.items()
            return list(enumerate(data, start=start))
        raise NotImplementedError("datatype is not a dictionary or list ")

    @staticmethod
    def strip_and_lower(string):
        """Return strip and lower value"""
        return str(string).lower().strip()

    @classmethod
    def lowered_dict(cls, data):
        """Strip and lower keys in dictionary"""
        if not cls.isDict(data):
            raise NotImplementedError("datatype is not a dictionary")

        item = {}
        for key, val in data.items():
            item[cls.strip_and_lower(key)] = val
        return item

    @classmethod
    def lowered_list(cls, data):
        """Strip and lower string in list"""
        if not cls.isList(data):
            raise NotImplementedError("datatype is not a List")
        return [cls.strip_and_lower(x) for x in data]


class Filter:
    @classmethod
    def choices(cls, choice, options, fallback=None):
        """Filter user choices and return the corresponding options
        Args:
            choice (str) - Expected choice
            options (list,tuple,dict):  Collection of options to select from.
            fallback (str,int, optional): Fallback choice if original expected choice
                                          is not found.
        """
        choice = Object.strip_and_lower(choice)
        if Object.isDict(options):
            options = Object.lowered_dict(options)
            val = [val for key, val in options.items() if choice in key]
        elif Object.isList(options):
            val = [val for val in options if choice == Object.strip_and_lower(val)]
        else:
            val = options if choice == Object.strip_and_lower(options) else fallback

        if not val and fallback:
            return cls.choices(fallback, options=options, fallback=None)

        elif val:
            return min(val)

    @staticmethod
    def by_int(choice, data):
        """
        Filter choices by integer
        :params:: choice,data
            choice - user choice. datatype: str
            data - list or dict object
        """
        try:
            choice = int(choice)
            results = Object.enumerate_it(data)
            if Object.isDict(data):
                return results[choice][1][1]
            return results[choice][1]
        except:
            return

    @classmethod
    def get_index(cls, index, options):
        """Filter options by index."""
        options_size = len(options)
        index -= 1
        index = 0 if (0 >= index or index > options_size) else index
        return index

    @classmethod
    def get_indexOf(cls, choice, options):
        for option in options:
            value = cls.choices(choice, option)
            if value:
                return option.index(value)
