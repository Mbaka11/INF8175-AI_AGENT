from .definition import AlgorithmHeuristic, Heuristic,ARGS_KEYS
from .constant import *
from .helper import *

class PointDifferenceHeuristic(AlgorithmHeuristic):

    def __init__(self):
        super().__init__(-18, 18)

    def _evaluation(self, current_state, **kwargs):        
        my_score =current_state.get_scores()[kwargs['my_id']]
        opponent_score =current_state.get_scores()[kwargs['opponent_id']]
        return my_score - opponent_score
    

class ControlIndexHeuristic(AlgorithmHeuristic):

    def _evaluation(self, current_state, **kwargs):
        ...

