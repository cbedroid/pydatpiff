"""
    This file will stored all dynamic class and methods.
    These methods will be used throughout the whole program.

"""
import concurrent.futures as cf
import sys  # noqa: F401
import threading
from functools import wraps

from pydatpiff.utils.request import Session


def Threader(f):
    @wraps(f)
    def inner(*a, **kw):
        t = threading.Thread(target=f, args=(a), kwargs=dict(kw))
        t.daemon = True
        t.start()
        return t

    return inner


class Queued:
    THREAD_COUNT = 75

    def __init__(self, main_job, input_work, *args, **kwargs):
        self.input = input_work  # work to put in queue
        self.main_job = main_job  # job to perform with work
        # song to search for TODO: move this to main function
        self.results = []
        self.args = args
        self.kwargs = kwargs
        self.thread_pool = []

    def run(self, *args, **kwargs):
        with cf.ThreadPoolExecutor() as ex:
            if args or kwargs:
                args = tuple(args) * len(self.input)
                kwargs = list(dict(kwargs) for _ in range(len(self.input)))
                data = ex.map(self.main_job, self.input, args, kwargs)
            else:
                data = ex.map(self.main_job, self.input)
        return [x for x in data]

    @classmethod
    def _setup(cls):
        """Stops the requests session from timing out before queue is finish"""
        cls._session_timeout = Session.TIMEOUT
        Session.TIMEOUT = 60

    @classmethod
    def _teardown(cls):
        """Sets the requests Session back to its original timeout"""
        Session.TIMEOUT = cls._session_timeout

    def capture_threads(self, threads):
        self.thread_pool.append(threads)

    def kill_all_threads(self):
        for t in self.thread_pool:
            if t.is_Alive():
                t.terminate()

    def set_queue(self):
        if Object.isList(self.input):
            # setting the queue from ^
            for obj in self.input:  # |
                self.q.put(obj)

    def put_worker_to_work(self):
        worker = self.q.get()
        if self.search:
            self.results.append(self.main_job(worker, self.search))
        else:
            self.results.append(self.main_job(worker))
        self.q.task_done()

    def start_thread(self):
        try:
            for _ in range(self.THREAD_COUNT):
                t = self.mp.map(self.put_worker_to_work)
                self.capture_threads(t)
                t.daemon = True
                t.start()
        except:
            self.kill_all_threads()
            self.start_thread()

    def run2(self):
        """Old threading method"""
        self._setup()
        self.set_queue()
        while True:
            self.start_thread()
            if self.q.empty():
                break
        # data will not be filter here for 'None type' in list
        # must catch all None types in the base method
        self._teardown()
        return self.results


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


class Selector:
    @staticmethod
    def filter_choices(choice, data):
        """
        Parse user string choice and return the corresponding data
        :params:: choice,data
            choice - user choice. datatype: str
            data - list or dict object
        """
        choice = Object.strip_and_lower(choice)
        if Object.isDict(data):
            data = Object.lowered_dict(data)
            val = [val for key, val in data.items() if choice in key]
        else:
            val = [val for val in data if choice in Object.strip_and_lower(val)]

        if val:
            return min(val)

    @staticmethod
    def choice_is_int(choice, data):
        """
        Parse user int choice and return the corresponding data
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
    def select_from_index(cls, select, data, *args):
        """select ablums_link by artist name, album name ('title')
        or by index number of title or artist
        """
        data_size = len(data)
        # checking from index
        select -= 1

        # catch index errors if user choose a mixtape out of range
        select = 0 if (0 >= select or select > data_size) else select
        return select

    @classmethod
    def select_from_choices(cls, select, *args):
        for choice in args:
            value = cls.filter_choices(select, choice)
            if value:
                return choice.index(value)
