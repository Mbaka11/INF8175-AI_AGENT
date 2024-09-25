
from enum import Enum
from functools import wraps
from typing import Any, Literal, Callable
from json import dump
from inspect import signature
from time import perf_counter

# Utils           ###########################################3


def hash_args(args):
    a, k = args
    return str(a)+"<==>"+str(k)


# Seeker              ###########################################3
class SeekerResultMode(Enum):
    PRINT = 'print'
    JSON = 'json'


class Seeker:

    TIME_KEY = 'time'
    COUNT_KEY = 'count'
    RESULT_KEY = 'result'

    Cache = {}

    def __init__(self, mode: SeekerResultMode = SeekerResultMode.JSON) -> None:
        self.mode = mode

    def init(self, func: Callable) -> None:
        self.seek_name = func.__name__
        self.func = func
        self.data: dict[Any, dict[str, int | float]] = {}
        self.total_time = 0
        self.calling_counter = 0
        self.parameter = signature(func).parameters
        Seeker.Cache[self.seek_name] = self

    def add(self, args, time, result=None):
        args = hash_args(args)
        self.calling_counter += 1
        self.total_time += time
        if args not in self.data:
            self.data[args] = {
                Seeker.TIME_KEY: time,
                Seeker.COUNT_KEY: 1,

            }
            return
        self.data[args][Seeker.COUNT_KEY] += 1
        self.data[args][Seeker.TIME_KEY] += time

    def __getitem__(self, args):
        args = hash_args(args)
        return self.data[args]

    def __delitem__(self, args):
        args = hash_args(args)
        self.data.pop(args)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        ...

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __contains__(self, args):
        return hash_args(args) in self.data

    @property
    def reuse_ratio(self):
        return 100-(self.__len__()*100/self.calling_counter)

    def __repr__(self) -> str:
        try:
            return f'Seeker(Function: {self.func}, Name: {self.seek_name},\n\t\tCalling_Counter: {self.calling_counter}, Total_Time: {self.total_time}, Reuse_Ratio: {self.reuse_ratio:0.4f}%, Distinct_Call: {self.__len__()} )'
        except ZeroDivisionError:
            return 'Target function has not been called yet'

    def __str__(self) -> str:
        try:
            print(
                f'Time Potentially Saved: {(self.reuse_ratio/100)*self.total_time}')
        
            dump({"parameter": str(self.parameter),
                "data": self.data}, open(self.seek_name+".json", 'w'))
            print(f'{self.func} Data Saved')
            return self.__repr__()
        except ZeroDivisionError: 
            return 'Target function has not been called yet'
        except AttributeError:
            return 'Object has not been initialized... Make sure to put in the Seek decorator'

    def __add__(self, other: object):
        ...

    def order(self, key: Literal['time', 'count']):
        return sorted(self.data.items(), key=lambda item: item[1][key])

    def max(self, key: Literal['time', 'count'] = 'count'):
        return f'Max({key}): {self.order(key) [-1]}'

    def min(self, key: Literal['time', 'count'] = 'count'):
        return f'Min({key}): {self.order(key)[0]}'


def Seek(seeker: Seeker):
    def decorator(func: Callable):
        seeker.init(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = perf_counter()
            result = func(*args, **kwargs)
            end_time = perf_counter()
            seeker.add((args, kwargs), end_time-start_time)
            return result
        return wrapper
    return decorator
##############################################                  ###########################################


def Time(func: Callable):

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()
        print(
            f'Time {func.__name__} - {hash_args((args,kwargs))}: {end_time-start_time} sec')
        return result

    return wrapper

##############################################  Memoirization     ###########################################


def Memoirization(func: Callable):
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = hash_args((args, kwargs))
        if key not in cache:
            cache[key]= func(*args, **kwargs)
        return cache[key]
    return wrapper


##############################################                 ###########################################



