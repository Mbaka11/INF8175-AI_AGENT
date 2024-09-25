
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

    Cache ={}

    def __init__(self, func: Callable) -> None:
        self.seek_name = func.__name__
        self.func = func
        self.data: dict[Any, dict[str, int | float]] = {}
        self.total_time = 0
        self.calling_counter = 0
        self.parameter = signature(func).parameters
        Seeker.Cache[self.seek_name] = self

    def add(self, args, time, result=None):
        args = self.hash_args(args)
        if args not in self.data:
            self.data[args] = {
                Seeker.TIME_KEY: time,
                Seeker.COUNT_KEY: 1,

            }
            return
        self.data[args][Seeker.COUNT_KEY] += 1
        self.data[args][Seeker.TIME_KEY] += time
        self.calling_counter += 1
        self.total_time += time

        self._ordered = False

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
        return f'Seeker(Function: {self.func}, Name: {self.seek_name},\nCalling_Counter: {self.calling_counter}, Total_Time: {self.total_time:0.5f}%, Reuse_Ratio: {self.reuse_ratio}, Distinct_Call: {self.__len__()} )'

    def __str__(self) -> str:
        dump(self.data, open(self.seek_name, 'w'))
        print(f'{self.func} Data Saved')
        return self.__repr__()

    def __add__(self, other: object):
        ...

    def order(self):
        self.data =  dict(sorted(self.data,key=lambda item:item[Seeker.COUNT_KEY]))
        self._ordered = True

    @property
    def max(self):
        if not self._ordered:
            self.order()
        return self.data[len(self)-1]        

    @property
    def min(self):
        if not self._ordered:
            self.order()
        return self.data[0]   
        

def Seek(func: Callable):
    seeker = Seeker(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        seeker.add((args, kwargs), end_time-start_time)
        return result
    return wrapper
