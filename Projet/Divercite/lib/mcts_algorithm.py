from dataclasses import dataclass
from game_state_divercite import GameStateDivercite
from .definition import Algorithm
from seahorse.game.light_action import LightAction

'''
So I restricted the total number of iterations to 6 so that after the 6th iteration, 
I could get a finite value for all these 6 nodes without creating further child nodes with branches.
'''


#@dataclass
class Node:


    def __init__(self, parent,action:LightAction):
        self.V = 0
        self.visit =0
        self.parent: Node = parent
        self.children: list[Node] = []
        self.action =action
    
    @property
    def ucb1(self) -> float:
        ...
    



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