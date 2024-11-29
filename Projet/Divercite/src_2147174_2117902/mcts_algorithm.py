from dataclasses import dataclass

from cachetools import Cache
from game_state_divercite import GameStateDivercite
from .definition import Algorithm, AlgorithmHeuristic, LossFunction, TimeConvertException, NegativeOrNullTimeException,StochasticActionInterface,DistributionType
from seahorse.game.light_action import LightAction
from random import choice
from time import time
from pytimeparse import parse
from .constant import MAX_STEP

'''
So I restricted the total number of iterations to 6 so that after the 6th iteration, 
I could get a finite value for all these 6 nodes without creating further child nodes with branches.
'''


# @dataclass
class Node:

    def __init__(self, state: GameStateDivercite,action_taken:LightAction=None, parent=None):
        self.value = 0
        self.visit = 0
        self.action_taken = action_taken
        self.parent: Node = parent
        self.children: list[Node] = []
        self.state: GameStateDivercite = state
        self.max_children: int = len(self.state.get_possible_light_actions())

    @property
    def is_fully_expanded(self):
        return len(self.children) >= self.max_children

    @property
    def ucb1(self) -> float:
        ...


class MCTSHybridMinimaxBackupsSearch(Algorithm,StochasticActionInterface):
    def __init__(self, typeB_heuristic:AlgorithmHeuristic,allowed_time: str, distribution_type:DistributionType,std:float=None,n_playouts:int=1,cache: int | Cache = 5000, max_depth: int | None = None, utility_type: LossFunction = 'diff',):
        allowed_time = self._convert_to_seconds(allowed_time)
        super().__init__(utility_type, typeB_heuristic, cache, allowed_time)
        self.max_depth = max_depth
        self.n_simulation = 0
        StochasticActionInterface.__init__(self,typeB_heuristic,distribution_type,std)
        self.n_playouts = n_playouts
    
    def _pred_utility(self, state:GameStateDivercite):
        total_pred =0
        for _ in range(self.n_playouts):
            if self._simulate(state)>0:
                total_pred+=1

        return total_pred

    def _search(self) -> LightAction:
        root_node = Node(self.current_state)
        start_time = time()

        while time() - start_time <= self.allowed_time:
            node: Node = self._select(root_node)
            reward = self._pred_utility(node.state)
            self._back_propagate(node, reward)
            self.n_simulation += 1

        # for _ in range(self.n_simulation):
        #     ...
        # TODO best_child based on some type of score, UCT1,UCTtuned, UCTminimax, 
        return self._best_action(root_node).state

    def _select(self,node:Node) -> Node:
        while not node.state.is_done():
            if not node.is_fully_expanded():
                return self._expand(node)
            else:
                node = self._best_action(node)
        return node

    def _expand(self,node:Node):
        tried_actions = {child.action_taken for child in node.children if child.action_taken != None }
        legal_actions = node.state.get_possible_light_actions()
        for action in legal_actions:
            if action not in tried_actions:
                next_state = self._transition(node.state,action)
                # Use cache to avoid redundant node creation

                if self.cache != None:
                    hash_state = self._hash_state(next_state.rep.env)
                    if hash_state not in self.cache:
                        flag, _hash = self.check_symmetric_moves_in_cache(
                            next_state.rep.env)
                        if flag:
                            hash_state = _hash
                        else:
                            self.cache[hash_state] = Node(next_state, action_taken=action,parent=node)

                    child_node = self.cache[hash_state]        
                    node.children.append(child_node)
                else :
                    child_node = Node(next_state, action_taken=action,parent=node)
                    node.children.append(child_node)
                
                return child_node

    def _back_propagate(self, node: Node, reward: float):
        while node is not None:
            node.visit += 1
            node.value += reward
            node = node.parent

    def _best_action(self,node:Node)->Node:
        ...

    def _convert_to_seconds(self, time_: str | int | float):
        try:
            if not isinstance(time_, str):
                return time_
            seconds = parse(time_)
            if seconds is not None:
                if seconds <= 0:
                    raise NegativeOrNullTimeException(seconds)
                return seconds
            raise TimeConvertException(f'Could not parse time string: {time_}')

        except Exception as e:
            raise TimeConvertException(
                f'Error while parsing time string: {time_}')
