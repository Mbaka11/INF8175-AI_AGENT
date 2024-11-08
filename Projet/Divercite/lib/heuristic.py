from abc import abstractmethod
from typing import Literal, Any
from game_state_divercite import GameStateDivercite
#from cachetools import FIFOCache,LFUCache,TTLCache,LRUCache,cachedmethod, Cache
import numpy as np
from seahorse.game.light_action import LightAction,Action
from random import choice,shuffle
from .constant import *

Method =Literal['min','max','mean','sum']

method = {
    'min':np.min,
    'max':np.max,
    'mean':np.mean,
    'sum':np.sum,
}

L=4.2

############################################ Base Heuristic class  #############################################

class Heuristic:
    def evaluate(self,current_state:GameStateDivercite,)-> Any:
        ...
    
    def __call__(self, *args, **kwds) -> LightAction | float:
        return self.evaluate(*args,**kwds)


class AlgorithmHeuristic(Heuristic):
    
    def __init__(self,min_value:float,max_value:float,method:Method='sum'):
        self.h_list:list[AlgorithmHeuristic] = [self]
        self.method = method
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, *args, **kwds) -> float:
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

class SimpleMoveHeuristic(Heuristic):

    def _check_city_in_center(self,pos,index_compute,preferred_pos = no_corner_city_position,fallback_pos = None):
             
        if fallback_pos == None:
            fallback_pos = preferred_pos
        new_pos = None
        n_index = len(index_compute)
        shuffle(index_compute)

        for index in range(n_index):
            i,j = index_compute[index]
            x,y = pos  
            new_pos = x+i,y+j
            if new_pos in preferred_pos:
                return new_pos
        
        return choice(fallback_pos)

    def _minimize_distance(self,):
        available_nice_city_position = list(set(no_corner_city_position).difference(self.moves))
        available_nice_city_position = np.array(available_nice_city_position)
        ...

#############################################  Random Test Heuristic ##############################################33
