from .definition import AlgorithmHeuristic, Heuristic,ARGS_KEYS
from .constant import *
from .helper import *

class PointDifferenceHeuristic(AlgorithmHeuristic):

    def __init__(self):
        super().__init__(-30, 30,L=6)

    def _evaluation(self, current_state, **kwargs):        
        my_state_score =current_state.get_scores()[kwargs['my_id']]
        opponent_state_score =current_state.get_scores()[kwargs['opponent_id']]

        my_current_score = kwargs['my_score']
        opponent_current_score = kwargs['opponent_score']

        my_delta_score =  my_state_score - my_current_score
        delta_state = my_state_score - opponent_state_score 
        cross_diff = (my_state_score - opponent_current_score) - (opponent_state_score-my_current_score)

        return my_delta_score+delta_state+cross_diff



class ControlIndexHeuristic(AlgorithmHeuristic):

    def _evaluation(self, current_state, **kwargs):
        ...

class RessourcesVarianceHeuristic(AlgorithmHeuristic):
    ...