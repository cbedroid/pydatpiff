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


def threader_wrapper(f):
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
    def is_dict(_type):
        return isinstance(_type, dict)

    @staticmethod
    def is_string(_type):
        return isinstance(_type, str)

    @staticmethod
    def is_list(_type):
        return isinstance(_type, list)

    @classmethod
    def remove_none_value(cls, _list):
        return list(filter(None, _list))

    @classmethod
    def enumerate_it(cls, data, start=0):
        """Return enumerate object"""
        if cls.is_dict(data) or cls.is_list(data):
            if cls.is_dict(data):
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
        if not cls.is_dict(data):
            raise NotImplementedError("datatype is not a dictionary")

        item = {}
        for key, val in data.items():
            item[cls.strip_and_lower(key)] = val
        return item

    @classmethod
    def lowered_list(cls, data):
        """Strip and lower string in list"""
        if not cls.is_list(data):
            raise NotImplementedError("datatype is not a List")
        return [cls.strip_and_lower(x) for x in data]


class Select:
    @classmethod
    def by_choices(cls, choice, options, fallback=None):
        """Select user choices and return the corresponding options
        Args:
            choice (str) - Expected choice
            options (list,tuple,dict):  Collection of options to select from.
            fallback (str,int, optional): Fallback choice if original expected choice
                                          is not found.
        """
        choice = Object.strip_and_lower(choice)

        try:

            if Object.is_dict(options):
                return min([val for key, val in options.items() if choice in Object.strip_and_lower(key)])

            elif Object.is_list(options):
                return min([val for val in options if choice in Object.strip_and_lower(val)])

            elif Object.is_string(options):
                return options if choice in Object.strip_and_lower(options) else fallback

        except ValueError:
            if fallback:  # no value found, then return fallback
                return cls.by_choices(fallback, options=options, fallback=None)
            raise ValueError("No value found for {}".format(choice))

    @staticmethod
    def by_int(choice, data):
        """
        Select choices by integer
        :params:: choice,data
            choice - user choice. datatype: str
            data - list or dict object
        """
        try:
            choice = int(choice)
            results = Object.enumerate_it(data)
            if Object.is_dict(data):
                return results[choice][1][1]
            return results[choice][1]
        except:
            pass

    @classmethod
    def get_index(cls, index, options):
        """Select options by an index."""
        options_size = len(options)
        index -= 1
        index = 0 if (0 >= index or index > options_size) else index
        return index

    @classmethod
    def get_index_of(cls, choice, options):
        """
        Performs a per option, case-insensitive search on each option and return index of options that matches partial
        or whole string.
        e,g:
            options = ['apple', 'orange', 'grape']
            choice = 'org' or "orange"
            return 1

        :params:: choice,options
            choice - user choice. datatype: str
            options - list or dict object

        Returns:
            index of options
        """
        for option in options:
            value = cls.by_choices(choice, option)
            if value:
                return options.index(value)
        raise ValueError("Choice not found")
