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

Method = Literal['min', 'max', 'mean', 'sum']

method = {
    'min': np.min,
    'max': np.max,
    'mean': np.mean,
    'sum': np.sum,
}

L = 4.2

ARGS_KEYS= Literal['opponent_score','my_score','last_move','my_piece','opponent_pieces']

############################################ Base Heuristic class  #############################################


class Heuristic:
    def evaluate(self, current_state: GameStateDivercite,**kwargs) -> Any:
        ...

    def __call__(self, *args, **kwds) -> LightAction | float:
        return self.evaluate(*args, **kwds)


class AlgorithmHeuristic(Heuristic):

    def __init__(self, min_value: float, max_value: float):
        self.h_list: list[AlgorithmHeuristic] = [self]
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, *args, **kwds) -> float: 
        if len(self.h_list) == 1:
            return self.evaluate(*args,**kwds)

        vals = [h.evaluate(*args,**kwds) for h in self.h_list]
        return sum(vals) # TODO add weighted sum 

    def evaluate(self, current_state: GameStateDivercite,**kwargs) -> float:
        return self._sigmoid(self._evaluation(current_state,**kwargs))

    def _evaluation(self,current_state:GameStateDivercite,**kwargs)-> float:
        ...

    def _sigmoid(self, x: float):
        x_scaled = (x - (self.min_value + self.max_value) / 2) / \
            ((self.max_value - self.min_value) / 2) * L
        return 2 / (1 + np.exp(-x_scaled)) - 1

    def __add__(self, other):
        if other not in self.h_list:
            self.h_list.append(other)

############################################# Base Strategy Classes ##############################################

class Strategy:

    # Meta Data
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

    def __init__(self, heuristic: Heuristic = None):
        self.main_heuristic = heuristic

    def search(self)-> LightAction:
        collect()
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

    def __init__(self, heuristic: AlgorithmHeuristic, cache: Cache, allowed_time: float = None):
        super().__init__(heuristic)
        self.cache = cache
        self.allowed_time = allowed_time

    def _utility(self, state: GameStateDivercite):
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

    def _transition(self, state: GameStateDivercite, action):
        return state.apply_action(action)

    def _compute_redondant_state(self, states: GameStateDivercite) -> Generator:
        # TODO
        return states.generate_possible_light_actions()

    def _hash_state(self, state: GameStateDivercite,next_max_depth:int) -> int:
        temp_env ={pos:piece.piece_type for pos, piece in state.rep.env.items()}
        return frozenset(temp_env.items())
        

