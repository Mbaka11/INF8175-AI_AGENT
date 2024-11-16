from abc import abstractmethod
from typing import Literal, Any
from game_state_divercite import GameStateDivercite
# from cachetools import FIFOCache,LFUCache,TTLCache,LRUCache,cachedmethod, Cache
import numpy as np
from seahorse.game.light_action import LightAction, Action
from random import choice, shuffle
from .constant import *
from .helper import *
from typing import Generator
from game_state_divercite import GameStateDivercite
from cachetools import FIFOCache, LFUCache, TTLCache, LRUCache, cachedmethod, Cache
from gc import collect
from seahorse.utils.custom_exceptions import ActionNotPermittedError

L = 4.1

ARGS_KEYS= Literal['opponent_score','my_score','last_move','my_pieces','opponent_pieces','moves','is_first_to_play','my_id','opponent_id','current_env']

############################################ Base Heuristic class  #############################################


class Heuristic:
    def evaluate(self, current_state: GameStateDivercite,**kwargs) -> Any:
        ...

    def __call__(self, *args, **kwds) -> LightAction | float:
        return self.evaluate(*args, **kwds)


class AlgorithmHeuristic(Heuristic):
    # BUG Need tweak for the weights adds

    def __init__(self, min_value: float, max_value: float,L=L,weight=1,h_list=None):
        self.h_list: list[AlgorithmHeuristic] = [self] if h_list ==None else h_list
        self.min_value = min_value
        self.max_value = max_value
        self.weight = weight
        self.total_weight=weight
        self.L = L

    def __call__(self, *args, **kwds) -> float: 
        if len(self.h_list) == 1:
            return self.evaluate(*args,**kwds)

        vals = [h.weight*h.evaluate(*args,**kwds) for h in self.h_list]
        return sum(vals)/self.total_weight # TODO add weighted sum 

    def evaluate(self, current_state: GameStateDivercite,**kwargs) -> float:
        return self._sigmoid(self._evaluation(current_state,**kwargs))

    def _evaluation(self,current_state:GameStateDivercite,**kwargs)-> float:
        ...

    def _sigmoid(self, x: float):
        x_scaled = (x - (self.min_value + self.max_value) / 2) / \
            ((self.max_value - self.min_value) / 2) * self.L
        return 2 / (1 + np.exp(-x_scaled)) - 1

    def __mul__(self,weight):
        # BUG if there is other parameter then change the __mul__ in the kid class
        clone = self.__class__()
        clone.weight = weight
        return clone

    def __truediv__(self,weight):
        clone = self.__class__()
        clone.weight = weight
        return clone

    def __add__(self, other):
        other:AlgorithmHeuristic = other
        total_weight =self.weight + other.weight
        temp = self.h_list + other.h_list
    
        clone = AlgorithmHeuristic(1,1,1,h_list=temp)
        clone.total_weight = total_weight
        return clone
    
    def __repr__(self):
        return f'{self.__class__.__name__}:{self.weight}'
    

############################################# Base Strategy Classes ##############################################


class Strategy:

    # Meta Data de l'État actuel
    is_first_to_play: bool = None
    current_state: GameStateDivercite = None
    my_id: int = None
    opponent_id: int = None
    remaining_time: float = None
    my_step: int = -1  # [0,19]

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

    def __init__(self, heuristic: AlgorithmHeuristic, cache: Cache=None, allowed_time: float = None,keep_cache: bool = False):
        super().__init__(heuristic)
        # if isinstance(cache,type):
        #     if cache_size ==None:
        #         cache_size = 500*max_depth
        #     cache = cache(cache_size)
        self.cache = cache
        self.allowed_time = allowed_time
        self.keep_cache = keep_cache # ERROR can be source of heuristic evaluation error, only uses if a deeper search was done prior a less deeper search

    def _utility(self, state: GameStateDivercite):
        scores = state.get_scores()
        my_scores = scores[self.my_id]
        opponent_scores = scores[self.opponent_id]

        # if my_scores > opponent_scores:
        #     return 1

        # if my_scores < opponent_scores:
        #     return -1

        # if my_scores == opponent_scores:
        #     return 0

        return my_scores-opponent_scores
        

    def _is_our_turn(self):
        if self.is_first_to_play and self.current_state.step % 2 == 0:
            return True

        if not self.is_first_to_play and self.current_state.step % 2 == 1:
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
