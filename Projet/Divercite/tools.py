
from enum import Enum
from functools import wraps
from typing import Any, Literal, Callable
from json import dump, dumps
import pprint
from inspect import signature
from time import time, time_ns

##############################################                  ###########################################3
class SeekerResultMode(Enum):
    PRINT = 'print'
    JSON = 'json'


class Seeker:

    TIME_KEY = 'time'
    COUNT_KEY = 'count'
    RESULT_KEY = 'result'

    Cache = {}

    def __init__(self, mode: SeekerResultMode=SeekerResultMode.JSON) -> None:
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
        args = self.hash_args(args)
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

    def hash_args(self, args):
        a, k = args
        return str(a)+"<==>"+str(k)

    def __getitem__(self, args):
        args = self.hash_args(args)
        return self.data[args]

    def __delitem__(self, args):
        args = self.hash_args(args)
        self.data.pop(args)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        ...

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return self.data

    @property
    def reuse_ratio(self):
        return 100-(self.__len__()*100/self.calling_counter)

    def __repr__(self) -> str:
        return f'Seeker(Function: {self.func}, Name: {self.seek_name},\n\t\tCalling_Counter: {self.calling_counter}, Total_Time: {self.total_time}, Reuse_Ratio: {self.reuse_ratio:0.4f}%, Distinct_Call: {self.__len__()} )'

    def __str__(self) -> str:
        dump(self.data, open(self.seek_name+".json", 'w'))
        print(f'{self.func} Data Saved')
        print(
            f'Time Potentially Saved: {(1-(self.reuse_ratio/100)*self.total_time)}')
        return self.__repr__()

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
            start_time = time()
            result = func(*args, **kwargs)
            end_time = time()
            seeker.add((args, kwargs), end_time-start_time)
            return result
        return wrapper
    return decorator
##############################################                  ###########################################3