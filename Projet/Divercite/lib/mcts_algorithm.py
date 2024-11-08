from game_state_divercite import GameStateDivercite
from .definition import Algorithm


class MCTSSearch(Algorithm):
    def __init__(self, heuristic, cache, allowed_time, max_depth:int,):
        super().__init__(heuristic, cache, allowed_time)
    
    def _init_tree(self):
        ...

    def _select(self):
        ...
    
    def _expend(self):
        ...
    
    def  _simulate(self):
        ...
    
    def _back_propagate(self):
        ...
    
    def _best_action(self):
        ...