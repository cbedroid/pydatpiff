"""
    This file will stored all dynamic class and methods.
    These methods will be used throughout the whole program. 
    
"""
import threading
from queue import Queue
from functools import wraps


class Queued():
    def __init__(self,main_job,input_work,search):
        self.input = input_work # work to put in queue
        self.main_job = main_job # job to perform with work
        # song to search for TODO: move this to main function
        self.search = search

        self.THREAD_COUNT = 75
        self.results = []
        self.q = Queue()

    def set_queue(self):
        if Datatype.isList(self.input):
            # setting the queue from ^
            for obj in self.input: #      |
                self.q.put(obj)


    def put_worker_to_work(self):
        worker = self.q.get()
        self.results.append(self.main_job(worker,self.search))
        self.q.task_done()


    def start_thread(self):
        for _ in range(self.THREAD_COUNT):
             t = threading.Thread(target = self.put_worker_to_work)
             t.daemon = True
             t.start()

    
    def run(self):
        self.set_queue()
        while True:
            self.start_thread()
            if self.q.empty():
                break
        # data will not be filter here for 'None type' in list
        # must catch all None type from the function called this method 
        return self.results




class Datatype():
    @staticmethod 
    def isDict(_type):
        return isinstance(_type,dict)

    @staticmethod 
    def isStr(_type):
        return isinstance(_type,str)

    @staticmethod 
    def isList(_type):
        return isinstance(_type,list)

    @classmethod
    def removeNone(cls,_list):
        if not cls.isList(_list):
            msg = 'Can not remove None value. ..datatype must be a list '
            raise NotImplementedError(msg)
        return list(filter(None,_list))

    @classmethod
    def enumerate_it(cls,data,start=0):
        """Return enumerate object"""
        if cls.isDict(data) or cls.isList(data):
            if cls.isDict(data):
                data = data.items()
            return list(enumerate(data,start=start))
        raise NotImplementedError('datatype is not a dictionary or list ')


    @staticmethod 
    def strip_lowered(string):
        """Return strip and lower value"""
        return str(string).lower().strip()


    @classmethod
    def lowered_dict(cls,data):
        """Strip and lower keys in dictionary"""
        if not cls.isDict(data):
            raise NotImplementedError('datatype is not a dictionary')

        item = {}
        for key,val in data.items():
            item[cls.strip_lowered(key)] =  val
        return item


    @classmethod
    def lowered_list(cls,data):
        """Strip and lower string in list"""
        if not cls.isList(data):
            raise NotImplementedError('datatype is not a List')
        return [cls.strip_lowered(x) for x in data]

class User():
    @staticmethod
    def choice_is_str(choice,data):
        """
        Parse user string choice and return the corresponding data
        :params:: choice,data 
            choice - user choice. datatype: str
            data - list or dict object
        """
        choice =  Datatype.strip_lowered(choice)
        if  Datatype.isDict(data):
            data =  Datatype.lowered_dict(data)
            val = [val for key,val in data.items() if choice in key] 
        else:
            val = [val for val in data if choice in  Datatype.strip_lowered(val)] 

        if val:
            return min(val)

    @staticmethod
    def choice_is_int(choice,data):
        """
        Parse user int choice and return the corresponding data
        :params:: choice,data 
            choice - user choice. datatype: str
            data - list or dict object
        """

        try:
            choice = int(choice)
            results =  Datatype.enumerate_it(data)
            length = len(data)
            if  Datatype.isDict(data):
                return results[choice][1][1]
            return results[choice][1]
        except Exception as e:
            print(e)
            return 


    @classmethod
    def selection(cls,select,byint=None,bystr=None):
        ''' select ablums_link by artist name, album name ('title')
         or by index number of title or artist
        '''
        try:
            # checking from index 
            if isinstance(select,int):
                select-=1
                length = len(byint) + 1
                # catch index errors if user choose a mixtape out of range
                select = 0 if (0 >= select or select > len(byint)) else select
                return select 

            else:
                #checking from artists
                choosen =  cls.choice_is_str
                choice = choosen(select,byint)
                if choice: return byint.index(choice)
                
                # check by mixtapes
                choice = choosen(select,bystr)
                if choice: return bystr.index(choice)

                if not choice: # will catch None value in Media
                   return 
                
        except BuildError as e:
            raise BuildError(1)

