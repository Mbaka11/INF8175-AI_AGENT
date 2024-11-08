from abc import abstractmethod
from typing import Literal, Any
from game_state_divercite import GameStateDivercite
#from cachetools import FIFOCache,LFUCache,TTLCache,LRUCache,cachedmethod, Cache
import numpy as np
from seahorse.game.light_action import LightAction,Action
from random import choice,shuffle
from .constant import *
from typing import Generator
from game_state_divercite import GameStateDivercite
from cachetools import FIFOCache,LFUCache,TTLCache,LRUCache,cachedmethod, Cache

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

############################################# Base Strategy Classes ##############################################

class Strategy:
    
    # Meta Data 
    is_first_to_play: bool = None
    current_state: GameStateDivercite = None
    my_id: int = None
    opponent_id: int = None
    remaining_time: float = None
    my_step:int = -1 # [0,19]

    
    @staticmethod
    def set_current_state(current_state:GameStateDivercite,remaining_time: float):
        Strategy.current_state = current_state
        Strategy.remaining_time = remaining_time
        Strategy.my_step+=1
        if Strategy.my_step == 0:
            Strategy.init_game_state()
        
    @staticmethod
    def init_game_state():
        Strategy.opponent_id = Strategy.current_state.compute_next_player().id
        temp = [ player.id for player in Strategy.current_state.players]
        temp.remove(Strategy.opponent_id)
        Strategy.my_id = temp[0]
        Strategy.is_first_to_play = Strategy.current_state.step == 0
        
    def __init__(self,heuristic: Heuristic=None):
        self.main_heuristic= heuristic

    def search(self):
        pass
    
    @property
    def my_pieces(self):
        return self.current_state.players_pieces_left[self.my_id]
    
    @property
    def opponent_pieces(self):
        return self.current_state.players_pieces_left[self.opponent_id]

    @property
    def my_score(self):
        return self.current_state.scores[self.my_id]

    @property
    def opponent_score(self):
        return self.current_state.scores[self.opponent_id]
    
    @property
    def last_move(self):
        return list(self.current_state.rep.env)[-1]
    
    @property
    def moves(self):
        return list(self.current_state.rep.env)

class Algorithm(Strategy):

    def __init__(self,heuristic:AlgorithmHeuristic,cache:Cache,allowed_time:float = None):
        super().__init__(heuristic)
        self.cache = cache
        self.allowed_time = allowed_time

    def _utility(self,state:GameStateDivercite):
        scores = state.get_scores()
        my_scores = scores[self.my_id]
        opponent_scores = scores[self.opponent_id]

        if my_scores > opponent_scores:
            return 1
        
        if my_scores < opponent_scores:
            return -1
        
        if my_scores == opponent_scores:
            return 0

    def _is_our_turn(self):
        if self.is_first_to_play and self.current_state.step % 2 == 0:
            return True
        
        if not self.is_first_to_play and self.current_state.step % 2 == 1:
            return True
        
        return False
             
    def _transition(self,state:GameStateDivercite,action):
        return state.apply_action(action)
    
    def _compute_redondant_state(self,states:list | Generator    ) -> Generator:
        # TODO 
        return states
    
    def _hash_state(self, state: GameStateDivercite) -> str:
        # TODO 
        ...