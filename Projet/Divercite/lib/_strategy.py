from typing import Generator
from .heuristic import Heuristic
from game_state_divercite import GameStateDivercite
from cachetools import FIFOCache,LFUCache,TTLCache,LRUCache,cachedmethod, Cache
import random

class Strategy:
    
    # Meta Data 
    is_first_move: bool = None
    current_state: GameStateDivercite = None
    my_id: int = None
    opponent_id: int = None
    remaining_time: float = None
    my_step:int = 0

    
    @staticmethod
    def set_current_state(current_state:GameStateDivercite,remaining_time: float):
        Strategy.current_state = current_state
        Strategy.remaining_time = remaining_time
        Strategy.my_step+=1
        print(Strategy.my_step)
        if Strategy.my_step == 1:
            Strategy.init_game_state()
        
    @staticmethod
    def init_game_state():
        Strategy.opponent_id = Strategy.current_state.compute_next_player().id
        temp = [ player.id for player in Strategy.current_state.players]
        temp.remove(Strategy.opponent_id)
        Strategy.my_id = temp[0]
        Strategy.is_first_move = Strategy.my_step == Strategy.current_state.step
        
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

class Algorithm(Strategy):

    def __init__(self,heuristic:Heuristic,cache:Cache,allowed_time:float):
        self.heuristic: Heuristic = heuristic
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
        if self.is_first_move and self.current_state.step % 2 == 0:
            return True
        
        if not self.is_first_move and self.current_state.step % 2 == 1:
            return True
        
        return False
             
    def _transition(self,state:GameStateDivercite,action):
        return state.apply_action(action)
    
    def _compute_redondant_state(self,states:list | Generator    ) -> Generator:
        # TODO 
        return states
    

class TestRandomAlgorithm(Strategy):

    def search(self):
        return random.choice(list(self.current_state.get_possible_heavy_actions()))
