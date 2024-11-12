from typing import Generator
from cachetools import Cache
from .definition import AlgorithmHeuristic, Algorithm
from game_state_divercite import GameStateDivercite
import numpy as np
from .constant import *
from gc import collect

class MinimaxTypeASearch(Algorithm):

    def __init__(self, typeA_heuristic: AlgorithmHeuristic, allowed_time: float, max_depth: int | None,cache: Cache):
        super().__init__(typeA_heuristic, cache, allowed_time)
        self.max_depth = max_depth
        self.hit = 0

    def search(self):
        super().search()
        _, action_star =self._minimax(self.current_state, True, float('-inf'), float('inf'),0,self.max_depth)
        return action_star

    def _minimax(self, state: GameStateDivercite, isMaximize: bool, alpha: float, beta: float,depth:int, max_depth: int = None):

        if state.is_done():
            return self._utility(state), None

        if depth >= max_depth:
            pred_utility = self.main_heuristic(
                state, my_id=self.my_id, opponent_id=self.opponent_id, my_pieces=self.my_pieces, opponent_pieces=self.opponent_pieces)
            if self._isQuiescent(state, pred_utility):
                return pred_utility, None

        v_star = float('-inf') if isMaximize else float('inf')
        m_star = None

        for action in self._compute_actions(state):

            new_state = self._transition(state,action)
            next_max_depth = self._compute_next_max_depth(
                max_depth, state.step, v_star, alpha, beta)

            if self.cache != None:
                
                hash_state = self._hash_state(new_state, next_max_depth) 
                if hash_state not in self.cache:
                    self.cache[hash_state]  = self._minimax(new_state, (not isMaximize), alpha, beta,depth+1, next_max_depth)

                v, _ = self.cache[hash_state]
            else:   
                v,_=self._minimax(new_state, (not isMaximize), alpha, beta,depth+1, next_max_depth)

            flag = (v>v_star) if isMaximize else (v<v_star)
            if flag:
                v_star = v
                m_star = action

            if isMaximize:
                alpha = max(alpha, v_star)
            else:
                beta = min(beta, v_star)

            if v_star >= beta and isMaximize:
                return v_star, m_star
            if v_star <= alpha and not isMaximize:
                return v_star, m_star

        return v_star, m_star

    def _isQuiescent(self, state: GameStateDivercite, pred_utility: float) -> bool:
        # TODO
        return True

    def _compute_next_max_depth(self, current_max_depth: int, current_step: int, v_star: float, alpha: float, beta: float) -> int:
        return current_max_depth

    def _compute_actions(self, state: GameStateDivercite):
       return  self._compute_redondant_state(state)


class MinimaxHybridSearch(MinimaxTypeASearch):

    def __init__(self, max_depth, cache: Cache, allowed_time: float, n_expanded: int, typeB_heuristic: AlgorithmHeuristic, typeA_heuristic: AlgorithmHeuristic = None):
        super().__init__(typeA_heuristic, cache, allowed_time, max_depth)
        self.n_expanded = n_expanded
        self.typeB_heuristic = typeB_heuristic
        if typeA_heuristic is None:
            self.main_heuristic = typeB_heuristic

    def _order_actions(self, actions: Generator | list, current_state: GameStateDivercite) -> list:
        # TODO modifier le nombre d'enfants a étendre dynamiquement
        vals = []
        returned_actions = []
        for a in actions:
            heavy_action = current_state.apply_action(a)
            returned_actions.append(a)
            vals.append(self.typeB_heuristic(heavy_action))

        vals = np.array(vals)
        returned_actions = np.array(returned_actions)
        n_child = len(vals)
        max_child_expanded = self.n_expanded if self.n_expanded < n_child else n_child
        vals = vals.argmax(axis=0)[:max_child_expanded]
        return returned_actions[vals]

    def _compute_actions(self, state: GameStateDivercite):
        actions = self._compute_redondant_state(state)
        return self._order_actions(actions, state)

    def _isQuiescent(self, state, pred_utility):
        # TODO If the step is less than the last step, we should check if the moves is safe
        return True

    def _compute_next_max_depth(self, current_max_depth: int, current_depth: int, v_star: int, alpha: float, beta: float):
        # TODO if we should go further or nah
        ...

    def _compute_max_n_expanded(self, cur_step):
        # TODO dynamically update the number of nodes expanded
        ...


class IterativeDeepeningSearch(Algorithm):
    ...
