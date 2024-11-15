from .definition import AlgorithmHeuristic, Heuristic,ARGS_KEYS
from .constant import *
from .helper import *
import numpy as np

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

class PiecesVarianceHeuristic(AlgorithmHeuristic):
    
    def __init__(self,city_weight=.7,ress_weight=.3):
        super().__init__(-300, -4,L=4.3)
        self.city_weight = city_weight
        self.ress_weight =ress_weight

    def _evaluation(self, current_state, **kwargs):
        opponent_pieces = current_state.players_pieces_left[kwargs['opponent_id']]
        my_pieces = current_state.players_pieces_left[kwargs['my_id']]

        my_original_pieces = kwargs['my_pieces']
        opponent_original_pieces = kwargs['opponent_pieces']

        #####

        my_original_var = self._pieces_var(my_original_pieces)
        opponent_original_var = self._pieces_var(opponent_original_pieces)

        my_state_var = self._pieces_var(my_pieces)
        opp_state_var = self._pieces_var(opponent_pieces)

        opp_diff = opp_state_var-opponent_original_var
        state_diff = opp_state_var-my_state_var
        my_diff = my_state_var-my_original_var
        #print(my_state_var)
        return -my_state_var
        
    def _pieces_var(self,pieces:dict[str,int]):
        city_val = np.array([pieces[cn] for cn in CityNames._member_names_])
        ress_val = np.array([pieces[rn] for rn in RessourcesNames._member_names_])
        score_city = np.var(city_val)*100
        score_ress = np.var(ress_val)*100

        score_city = 25 if score_city ==0 else score_city
        score_ress = 40 if score_ress ==0 else score_ress
        return (score_city*self.city_weight + score_ress*self.ress_weight)/self._h_tot_weight
        
        ##################################
        # city_val = np.var(city_val)
        # ress_val = np.var(ress_val)*1.05
        
        # ress_val = 0.5 if ress_val == 0 else ress_val
        #return -min(city_val, ress_val)
        #return float(city_val*self.city_weight+ ress_val*self.ress_weight)/self._h_tot_weight
        #return float(city_val+ress_val)
        ##########################
        # pieces_vectors = (city_val*self.city_weight + ress_val*self.ress_weight)/self._h_tot_weight
        # return float(np.var(pieces_vectors)*100)
        ############################################33

    
    @property
    def _h_tot_weight(self):
        return self.city_weight+self.ress_weight