from abc import abstractmethod
from typing import Literal, Any
from game_state_divercite import GameStateDivercite
#from cachetools import FIFOCache,LFUCache,TTLCache,LRUCache,cachedmethod, Cache
import numpy as np
from random import choice

Method =Literal['min','max','mean','sum']

method = {
    'min':np.min,
    'max':np.max,
    'mean':np.mean,
    'sum':np.sum,
}

L=4.2

class Heuristic:
    def evaluate(self,current_state:GameStateDivercite,)-> Any:
        ...
    
    def __call__(self, *args, **kwds):
        return self.evaluate(*args,**kwds)


class AlgorithmHeuristic(Heuristic):
    
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
        
    def evaluate(self,current_state:GameStateDivercite)-> float:
        ...

    def _sigmoid(self,x:float):
        x_scaled = (x - (self.min_value + self.max_value) / 2) / ((self.max_value - self.min_value) / 2) * L
        return 2 / (1 + np.exp(-x_scaled)) - 1

    def __add__(self,other):
        if other not in self.h_list: 
            self.h_list.append(other)

#############################################  Random Test Heuristic ##############################################33

class RandomTestHeuristic(Heuristic):

    def evaluate(self, current_state):
        return choice(list(self.current_state.get_possible_heavy_actions()))
