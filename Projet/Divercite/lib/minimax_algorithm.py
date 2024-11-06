from abc import abstractmethod
from .heuristic import Heuristic
from game_state_divercite import GameStateDivercite
from ._algorithm import Algorithm
import numpy as np

class MinimaxSearch(Algorithm):

    def __init__(self, typeA_heuristic:Heuristic,max_depth:int|None):
        super().__init__(typeA_heuristic)
        if max_depth == None:
            max_depth = self.current_state.max_step - self.current_state.step

        self.max_depth = max_depth

    def alphaBeta_search(self,depth):
        return self._minimax(self.current_state,True,float('-inf'),float('inf'),depth)
 
    def _minimax(self,state:GameStateDivercite,isMaximize:bool,alpha:float,beta:float,depth:int,max_depth:int = None):
        if max_depth == None:
            max_depth = self.max_depth
        
        if self._isTerminal(state,depth):
            return self._utility(state), None
        
        if depth >= max_depth:
            pred_utility= self.heuristic(state)
            if self._isQuiescent(state,pred_utility):
                return pred_utility,_

        v_star = float('-inf') if isMaximize else float('inf')
        m_star = None

        for action in self._compute_actions(state):
            new_state = self._transition(state,action)
            next_max_depth = self._compute_next_max_depth(max_depth,depth,v_star)
            v,_ =  self._minimax(new_state, not isMaximize,alpha, beta,depth+1,next_max_depth)
            if v >= v_star:
                v_star = v
                m_star = action

                if isMaximize:
                    alpha = max(alpha,v_star)
                else:
                    beta = min(beta,v_star)

                if v_star >= beta and isMaximize: return v_star,m_star
                if v_star <= alpha and not isMaximize: return v_star,m_star
        return v_star,m_star    

    @abstractmethod
    def _isQuiescent(self,state:GameStateDivercite, pred_utility:float)->bool:
        True
    
    @abstractmethod
    def _compute_next_max_depth(self,current_max_depth:int, current_depth:int,v_star:float) -> int:
        return current_max_depth

    @abstractmethod
    def _order_actions(self,states:list):
        return states
    
    def _compute_actions(self,state:GameStateDivercite):
        states = self._compute_redondant_state(state)
        return self._order_actions(states)


class MinimaxTypeBSearch(MinimaxSearch):

    def __init__(self,max_depth,n_expanded:int,typeB_heuristic:Heuristic,typeA_heuristic:Heuristic= None):
        super().__init__(typeA_heuristic, max_depth)  
        self.n_expanded = n_expanded
        self.typeB_heuristic = typeB_heuristic
        if typeA_heuristic is None:
            self.heuristic = typeB_heuristic
    
    def _order_actions(self, states):
        ...

    def _isQuiescent(self, state, pred_utility):
        ...

    def _compute_next_max_depth(self, current_max_depth, current_depth,v_star):
        ...