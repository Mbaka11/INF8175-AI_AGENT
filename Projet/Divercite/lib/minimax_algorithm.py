from typing import Generator

from cachetools import Cache
from .heuristic import Heuristic
from game_state_divercite import GameStateDivercite
from ._strategy import Algorithm
import numpy as np
from .constant import *
from gc import collect

class MinimaxTypeASearch(Algorithm):

    def __init__(self, typeA_heuristic:Heuristic,cache:Cache,allowed_time:float,max_depth:int|None):
        super().__init__(typeA_heuristic,cache,allowed_time)
        if max_depth == None:
            self.max_depth = MAX_STEP

        else:
            self.max_depth = self.current_state.step + max_depth
            if self.max_depth > MAX_STEP:
                print('Warning:','')
                self.max_depth = MAX_STEP


    def _alphaBeta_search(self):
        collect()
        return self._minimax(self.current_state,True,float('-inf'),float('inf'))
 
    def _predict_by_time(self):
        ... 
        
    def _minimax(self,state:GameStateDivercite,isMaximize:bool,alpha:float,beta:float,max_depth:int = None):
        if max_depth == None:
            max_depth = self.max_depth
        
        if state.is_done():
            collect()
            return self._utility(state), None
        
        if state.step >= max_depth:
            pred_utility= self.main_heuristic(state)
            if self._isQuiescent(state,pred_utility):
                collect()
                return pred_utility,_

        v_star = float('-inf') if isMaximize else float('inf')
        m_star = None

        for action in self._compute_actions(state):
            
            new_state = self._transition(state,action)
            next_max_depth = self._compute_next_max_depth(max_depth,state.step,v_star,alpha, beta)
        
            v,_ =  self._minimax(new_state, not isMaximize,alpha, beta,next_max_depth)
            if v >= v_star:
                v_star = v
                m_star = action

                if isMaximize:
                    alpha = max(alpha,v_star)
                else:
                    beta = min(beta,v_star)

                if v_star >= beta and isMaximize: return v_star,m_star
                if v_star <= alpha and not isMaximize: return v_star,m_star

        collect()
        return v_star,m_star    

    def _isQuiescent(self,state:GameStateDivercite, pred_utility:float)->bool:
        # TODO 
        True
    
    def _compute_next_max_depth(self,current_max_depth:int, current_step:int,v_star:float,alpha:float,beta:float) -> int:
        return current_max_depth

    def _order_actions(self,actions:list | Generator,current_state:GameStateDivercite,current_n:int)-> Generator | list:
        return actions
    
    def _compute_actions(self,state:GameStateDivercite):
        actions = self._compute_redondant_state(state)
        return self._order_actions(actions,state)

    def _compute_max_n_expanded(self, cur_step):
        return float('inf')


class MinimaxHybridSearch(MinimaxTypeASearch):

    def __init__(self,max_depth,cache:Cache,allowed_time:float, n_expanded:int,typeB_heuristic:Heuristic,typeA_heuristic:Heuristic= None):
        super().__init__(typeA_heuristic, cache,allowed_time,max_depth)  
        self.n_expanded = n_expanded
        self.typeB_heuristic = typeB_heuristic
        if typeA_heuristic is None:
            self.main_heuristic = typeB_heuristic
    
    def _order_actions(self, actions: Generator | list,current_state: GameStateDivercite) -> list:
        # TODO modifier le nombre d'enfants a etendre dynamiquement
        vals = []
        returned_actions = []
        for a in actions:
            heavy_action = current_state.apply_action(a)
            returned_actions.append(a)
            vals.append(self.typeB_heuristic(heavy_action))
        
        vals = np.array(vals)
        returned_actions = np.array(returned_actions)
        vals = vals.argmax()[self.n_expanded]
        return returned_actions[vals]

    def _isQuiescent(self, state, pred_utility):
        ...

    def _compute_next_max_depth(self, current_max_depth:int, current_depth:int,v_star:int,alpha:float,beta:float):
        ...
    
    def _compute_max_n_expanded(self, cur_step):
        ...

class IterativeDeepeningSearch(Algorithm):
    ...