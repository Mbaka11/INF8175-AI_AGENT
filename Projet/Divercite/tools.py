
from functools import wraps
from typing import Any, overload, Callable, MappingView
from json import dump, dumps
import pprint
from inspect import signature
from time import time, time_ns
from timeit import timeit


class Seeker:
    TIME_KEY = 'time'
    COUNT_KEY = 'count'
    RESULT_KEY = 'result'

    def __init__(self, func: Callable) -> None:
        self.seek_name = func.__name__
        self.data: dict[Any, dict[str, int | float]] = {}
        self.time = 0
        self.calling_counter = 0
        self.parameter = signature(func).parameters

    def add(self,args,time,result=None):
        args = self.hash_args(args)
        if args not in self.data:
            self.data[args] ={
                Seeker.TIME_KEY :time,
                Seeker.COUNT_KEY : 1,

            }
            return
        self.data[args][Seeker.COUNT_KEY]+=1
        self.data[args][Seeker.TIME_KEY]+=time
        self.calling_counter +=1
        self.time+=time

    def hash_args(self,args): 
        return str(args)

    def __getitem__(self, args):
        args = self.hash_args( args)
        return self.data[args]
    
    def __delitem__(self, args):
        args = self.hash_args( args)
        self.data.pop(args)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        ...
    
    def __len__(self):
        return len(self.data)
    
    @property
    def reuse_ratio(self):
        return self.__len__()*100/self.calling_counter
    
    def __repr__(self) -> str:
        pass
    
    def __str__(self) -> str:
        pass

    def __add__(self, other:object):
        ...


def Seek(func: Callable):
    seeker = Seeker(func)
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        seeker.add((args,kwargs), end_time-start_time)
        return result
    return wrapper
