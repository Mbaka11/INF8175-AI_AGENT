from abc import abstractmethod
from typing import Literal
from game_state_divercite import GameStateDivercite
#from cachetools import FIFOCache,LFUCache,TTLCache,LRUCache,cachedmethod, Cache
import numpy as np

Method =Literal['min','max','mean','sum']

method = {
    'min':np.min,
    'max':np.max,
    'mean':np.mean,
    'sum':np.sum,
}

L=4.2

class AlgorithmHeuristic:
    
    def __init__(self,min_value:float,max_value:float,method:Method='sum'):
        self.h_list:list[AlgorithmHeuristic] = [self]
        self.method = method
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, *args, **kwds):
        if len(self.h_list) ==1:
            return self.evaluate(*args)
        
        vals = [h.evaluate(*args) for h in self.h_list]
        return method[self.method](vals)
        
    @abstractmethod
    def evaluate(self,current_state:GameStateDivercite)-> float:
        ...

    def _sigmoid(self,x:float):
        x_scaled = (x - (self.min_value + self.max_value) / 2) / ((self.max_value - self.min_value) / 2) * L
        return 2 / (1 + np.exp(-x_scaled)) - 1

    def __add__(self,other):
        if other not in self.h_list: 
            self.h_list.append(other)

