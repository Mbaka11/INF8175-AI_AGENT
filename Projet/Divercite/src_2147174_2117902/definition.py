from abc import abstractmethod
from typing import Literal, Any
from game_state_divercite import GameStateDivercite
import numpy as np
from seahorse.game.light_action import LightAction, Action
from random import choice, shuffle
from .constant import *
from .helper import *
from typing import Generator
from game_state_divercite import GameStateDivercite
from cachetools import FIFOCache, LFUCache, TTLCache, LRUCache, cachedmethod, Cache,TLRUCache
from gc import collect
from seahorse.utils.custom_exceptions import ActionNotPermittedError
from enum import Enum
from inspect import signature

L = 4.1

class Optimization(Enum):
    MAXIMIZE = 1
    MINIMIZE = -1

ARGS_KEYS= Literal['opponent_score','my_score','last_move','my_pieces','opponent_pieces','moves','is_first_to_play','my_id','opponent_id','current_env']
Normalization_Type = Literal['range_scaling','sigmoid']
############################################ Base Heuristic class  #############################################


class Heuristic:
    def evaluate(self, current_state: GameStateDivercite,**kwargs) -> Any:
        ...

    def __call__(self, *args, **kwds) -> LightAction | float:
        return self.evaluate(*args, **kwds)


class AlgorithmHeuristic(Heuristic):
    
    def __init__(self,normalization_type:Normalization_Type, min_value: float, max_value: float,L=L,weight=1,h_list=None,optimization = Optimization.MAXIMIZE,):
        self.heuristic_list: list[AlgorithmHeuristic] = [self] if h_list ==None else h_list
        self.min_value = min_value
        self.max_value = max_value
        self.weight = weight
        self.total_weight=weight
        self.L = L
        self.optimization = optimization
        self.normalization_type:Normalization_Type = normalization_type


    def __call__(self, *args, **kwds) -> float: 
        if len(self.heuristic_list) == 1:
            return self.evaluate(*args,**kwds)
        
        vals = [hrstc.weight * hrstc.evaluate(*args,**kwds) for hrstc in self.heuristic_list]
        return sum(vals)/self.total_weight

    def evaluate(self, current_state: GameStateDivercite,**kwargs) -> float:
        state_eval = self._evaluation(current_state,**kwargs)
        return self.normalize(state_eval)

    def _evaluation(self,current_state:GameStateDivercite,**kwargs)-> float:
        ...

    def _sigmoid(self, x: float,min_value,max_value,L=L):
        x_scaled = (x - (min_value + max_value) / 2) / \
            ((max_value - min_value) / 2) * L
        return 2 / (1 + np.exp(-x_scaled)) - 1
    
    def normalize(self,x:float):
        if self.normalization_type == 'sigmoid':
            return self._sigmoid(x,self.min_value,self.max_value,self.L)
     
        return self._range_scaling(x,self.min_value,self.max_value)
        
    def _range_scaling(self,value, min_value, max_value):
        if min_value == max_value:
            raise ValueError("min_value and max_value must be different for scaling.")
        
        normalized_value = (value - min_value) / (max_value - min_value)
        scaled_value = 2 * normalized_value - 1
        return scaled_value
        
    def __mul__(self,weight):
        return self._clone(weight)

    def __truediv__(self,weight):
        return self._clone(weight)
    
    def _clone(self, weight):
        temp_args = self._compute_added_args()
        clone = self.__class__(**temp_args)
        clone.weight = weight
        #clone.h_list = self.h_list
        return clone
 
    def _compute_added_args(self):
        temp_args = self.__dict__.copy()

        del temp_args['weight']
        del temp_args['min_value']
        del temp_args['max_value']
        del temp_args['L']
        del temp_args['heuristic_list']
        del temp_args['optimization']
        del temp_args['total_weight']

        return temp_args
    
    def __add__(self, other):
        other:AlgorithmHeuristic = other
        total_weight =self.weight + other.weight
        temp = self.heuristic_list + other.heuristic_list

        clone = AlgorithmHeuristic(None,1,1,h_list=temp)
        clone.total_weight = total_weight
        return clone
    
    def __repr__(self):
        if len(self.heuristic_list) <= 1:
            return f'{self.__class__.__name__}:{self.weight}'
        return f'{self.__class__.__name__}:{self.total_weight} - {self.heuristic_list}'
    
    def _maximize_score_diff(self,my_current,opp_current,my_state,opp_state):
        my_delta_score = my_state - my_current
        delta_state = my_state - opp_state
        cross_diff = (my_state - opp_current) - \
            (opp_state-my_current)

        return my_delta_score+delta_state+cross_diff

    def _maximized_potential(self,opp_state,my_state):
        return self.optimization.value*((my_state - opp_state) + my_state)
            

############################################# Base Strategy Classes ##############################################


class Strategy:

    # Meta Data de l'État actuel
    is_first_to_play: bool = None
    current_state: GameStateDivercite = None
    my_id: int = None
    opponent_id: int = None
    remaining_time: float = None
    my_step: int = -1  # [0,19]
    my_piece_type:str=None
    opponent_piece_type:str=None
                
    @staticmethod
    def set_current_state(current_state: GameStateDivercite, remaining_time: float):
        Strategy.current_state = current_state
        Strategy.remaining_time = remaining_time
        Strategy.my_step += 1
        
        if Strategy.my_step == 0:
            Strategy.init_game_state()

    @staticmethod
    def init_game_state():
        Strategy.opponent_id = Strategy.current_state.compute_next_player().id
        temp = [player.id for player in Strategy.current_state.players]
        temp.remove(Strategy.opponent_id)
        Strategy.my_id = temp[0]
        Strategy.is_first_to_play = Strategy.current_state.step == 0
        Strategy.my_piece_type = W_PIECE if Strategy.is_first_to_play else B_PIECE
        Strategy.opponent_piece_type = list(PIECE_TYPE.difference([Strategy.my_piece_type]))[0]

    def __init__(self, heuristic: Heuristic|AlgorithmHeuristic = None):
        self.main_heuristic = heuristic

    @staticmethod
    def greedy_fallback_move():
        '''
        Code taken from the template
        '''

        possible_actions = Strategy.current_state.generate_possible_light_actions()
        best_action = next(possible_actions)
        best_score = Strategy.current_state.apply_action(best_action).scores[Strategy.my_id]

        for action in possible_actions:
            state = Strategy.current_state.apply_action(action)
            score = state.scores[Strategy.my_id]
            if score > best_score:
                best_action = action
        
        print('Error')
        return best_action

    def _search(self) -> LightAction:
        ...

    def search(self):
        collect()
        try:
            return self._search()
        except ActionNotPermittedError as e:
            print(e.__class__.__name__,f': {e.args}')
        except Exception as e:
            print('Warning... !:',e.__class__.__name__,f': {e.args}')
        
        return Strategy.greedy_fallback_move()

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
    
    @property
    def current_env(self):
        return self.current_state.rep.env


class Algorithm(Strategy):

    def __init__(self, heuristic: AlgorithmHeuristic, cache: int=None, allowed_time: float = None,keep_cache: bool = False):
        super().__init__(heuristic)
        if isinstance(cache,Cache):
            self.cache = cache
        else:
            self.cache = None if cache == None else LRUCache(cache)
        self.allowed_time = allowed_time
        self.keep_cache = keep_cache # ERROR can be source of heuristic evaluation error, only uses if a deeper search was done prior a less deeper search

    def _utility(self, state: GameStateDivercite):
        scores = state.get_scores()
        my_scores = scores[self.my_id]
        opponent_scores = scores[self.opponent_id]
        return my_scores-opponent_scores
        

    def _is_our_turn(self, step = None):
        if step ==None:
            step = self.current_state.step 

        if self.is_first_to_play and step % 2 == 0:
            return True

        if not self.is_first_to_play and step % 2 == 1:
            return True

        return False

    def _transition(self, state: GameStateDivercite, action):
        return state.apply_action(action)
    
    def rotate_moves_90(self,moves:dict[tuple[int,int],Any]):
        temp_moves = {}
        for pos, pieces in moves.items():
            x,y = pos
            pos = rotate_position_90_clockwise(x,y)
            temp_moves[pos] = pieces
        return temp_moves

    def _hash_state(self, state_env: dict) -> int:
        temp_env ={pos:piece.piece_type for pos, piece in state_env.items()}
        return frozenset(temp_env.items())
    
    def check_symmetric_moves_in_cache(self, state_env:dict) -> tuple[bool, None | frozenset]:   
        temp_env = state_env.copy()
        for _ in range(3):
            temp_env= self.rotate_moves_90(temp_env) 
            temp_env_hash = self._hash_state(temp_env)
            if temp_env_hash in self.cache:
                return True, temp_env_hash
        return False, None
    
    def _clear_cache(self):
        try:
            if self.cache != None and not self.keep_cache:
                self.cache.clear()
        except AttributeError:
            print('Warning: Trying to clear cache when None is provided')
        except:
            ...
        
    def search(self):
        # NOTE See comments in line 170
        self._clear_cache()
        return super().search()
