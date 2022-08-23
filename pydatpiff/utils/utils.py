"""
    This file will stored all dynamic class and methods.
    These methods will be used throughout the whole program.

"""
import sys  # noqa: F401
import threading
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import List, Tuple, Union


def threader_wrapper(f):
    @wraps(f)
    def inner(*a, **kw):
        t = threading.Thread(target=f, args=(a), kwargs=dict(kw))
        t.daemon = True
        t.start()
        return t

    return inner


class ThreadQueue:  # pragma: no cover
    def __init__(self, main_job, input_work: Union[Tuple, List], *args, **kwargs):
        """
        This class will be used to execute concurrent jobs.
        The main job will be executed with the input work.
        The input work will be a list of work to be executed.
        :param input_work: input work to perform the main job with.
        """
        self.main_job = main_job  # job to perform with work
        self.input_work = input_work

    def execute(self, *args, **kwargs):
        """
        This method will execute the main job with the input work.
        args and kwargs are additional arguments kwargs
        :param args: args to pass to the main job.
        :param kwargs: kwargs to pass to the main job.

        """
        with ThreadPoolExecutor(max_workers=3) as executor:
            if args or kwargs:
                data = executor.map(
                    lambda work: self.main_job(work, *args, **kwargs), [work for work in self.input_work], timeout=10
                )
            else:
                data = executor.map(self.main_job, self.input_work)
            executor.shutdown(wait=True)
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
        return isinstance(_type, (list, tuple))

    @staticmethod
    def strip_and_lower(string):
        """Return strip and lower value"""
        return str(string).lower().strip()

    @classmethod
    def remove_list_null_value(cls, _list):
        return list(filter(None, _list))

    @classmethod
    def enumerate_options(cls, data, start=0):
        """Return enumerate object"""
        if cls.is_dict(data) or cls.is_list(data):
            if cls.is_dict(data):
                data = data.items()
            return list(enumerate(data, start=start))
        raise NotImplementedError("datatype is not a dictionary or list ")


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
        val = None
        try:
            if Object.is_dict(options):
                val = min([key for key, val in options.items() if choice in Object.strip_and_lower(key)])

            elif Object.is_list(options):
                val = min([val for val in options if choice in Object.strip_and_lower(val)])

            elif Object.is_string(options):
                val = options if choice in Object.strip_and_lower(options) else fallback

            assert val is not None
        except ValueError:
            if fallback:  # no value found, then return fallback
                return cls.by_choices(choice=fallback, options=options, fallback=None)
            raise ValueError("No value found for {}".format(choice))
        return val

    @classmethod
    def get_leftmost_index(cls, index, options):
        """
        Select options by its index and return the left most index, or index minus 1.
        e.g. if index is 2 and options are [a,b,c,d,e] then return 1 (index 1).
               [a, b, c, d, e] , so index 2 = `c`, so leftmost is 1.

        """
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
        value = cls.by_choices(choice, options)
        if value:
            if Object.is_dict(options):
                options = list(options)
            return options.index(value)

        raise ValueError("Choice not found")
