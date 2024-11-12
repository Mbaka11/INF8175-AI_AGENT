from typing import Generator
from cachetools import Cache
from .definition import AlgorithmHeuristic, Algorithm
from game_state_divercite import GameStateDivercite
import numpy as np
from .constant import *
from gc import collect

class MinimaxTypeASearch(Algorithm):

    def __init__(self, typeA_heuristic: AlgorithmHeuristic, cache: Cache, allowed_time: float, max_depth: int | None):
        super().__init__(typeA_heuristic, cache, allowed_time)
        self.max_depth = max_depth

    def search(self):
        # if self.max_depth == None:
        #     self.max_depth = MAX_STEP

        # else:
        #     self.max_depth = self.current_state.step + self.max_depth
        #     if self.max_depth > MAX_STEP:
        #         self.max_depth = MAX_STEP

        _,best_action= self._minimax(self.current_state, 0,True, float('-inf'), float('inf'),self.max_depth)
        return best_action

    def _minimax(self, state: GameStateDivercite,depth:int, isMaximize: bool, alpha: float, beta: float, max_depth: int = None):
        
        if state.is_done():
            return self._utility(state), None

        if depth >= max_depth:
            print(state.step)
            pred_utility = self.main_heuristic(
                state, my_id=self.my_id, opponent_id=self.opponent_id, my_pieces=self.my_pieces, opponent_pieces=self.opponent_pieces)
            if self._isQuiescent(state, pred_utility):
                return pred_utility, _

        v_star = float('-inf') if isMaximize else float('inf')
        m_star = None

        for action in state.generate_possible_light_actions(): #NOTE this will change

            new_state = self._transition(state, action)
            next_max_depth = self._compute_next_max_depth(
                max_depth, state.step, v_star, alpha, beta)

            hash_state = self._hash_state(new_state, next_max_depth) # BUG Might not be the best hash_ function

            if hash_state not in self.cache:
                self.cache[hash_state] = self._minimax(
                    new_state, depth+1,(not isMaximize), alpha, beta, next_max_depth)

            v, _ = self.cache[hash_state]
            flag = (v > v_star) if isMaximize else (v<v_star)

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
        True

    def _compute_next_max_depth(self, current_max_depth: int, current_step: int, v_star: float, alpha: float, beta: float) -> int:
        return current_max_depth

    def _order_actions(self, actions: list | Generator, current_state: GameStateDivercite) -> Generator | list:
        return actions

    def _compute_actions(self, state: GameStateDivercite):
        actions = self._compute_redondant_state(state)
        return self._order_actions(actions, state)

    def _compute_max_n_expanded(self, cur_step):
        return float('inf')


class MinimaxHybridSearch(MinimaxTypeASearch):

    def __init__(self, max_depth, cache: Cache, allowed_time: float, n_expanded: int, typeB_heuristic: AlgorithmHeuristic, typeA_heuristic: AlgorithmHeuristic = None):
        super().__init__(typeA_heuristic, cache, allowed_time, max_depth)
        self.n_expanded = n_expanded
        self.typeB_heuristic = typeB_heuristic
        if typeA_heuristic is None:
            self.main_heuristic = typeB_heuristic

    def _order_actions(self, actions: Generator | list, current_state: GameStateDivercite) -> list:
        # TODO modifier le nombre d'enfants a etendre dynamiquement
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

    def _isQuiescent(self, state, pred_utility):
        # TODO If the step is less than the last step, we should check if the moves is safe
        ...

    def _compute_next_max_depth(self, current_max_depth: int, current_depth: int, v_star: int, alpha: float, beta: float):
        # TODO if we should go further or nah
        ...

    def _compute_max_n_expanded(self, cur_step):
        # TODO dynamically update the number of nodes expanded
        ...


class IterativeDeepeningSearch(Algorithm):
    ...
