from game_state_divercite import GameStateDivercite
from ._algorithm import Algorithm
from cachetools import FIFOCache,LFUCache,TTLCache

class MinimaxABSearch(Algorithm):

    def __init__(self, heuristic,max_depth:int,n_expanded:int):
        super().__init__(heuristic)
        self.max_depth = max_depth
        self.n_expanded = n_expanded
    
    def alphaBeta_search(self):
        ...

    def _turn(self):
        ...

    def _minimax(self,isMaximize:bool,alpha:float,beta:float,depth:int):
        ...

    def _isQuiescent(self):
        ...

    def _compute_redondant_state(self):
        ...

    def _is_evaluating(self):
        ...
    