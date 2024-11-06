from lib._algorithm import Algorithm
from .constant import *

class AlgoController:
    
    def __init__(self):
        self.strategy:list[Algorithm] = []
        self.strategy_count = 0

    def __call__(self, *args, **kwds):
        return self._play_best_move(*args)

    def _play_best_move(self, moves_index:int):
        algorithm = self[moves_index]
        return algorithm.compute_best_moves()
        
    def add_strategy(self, moves_index:int,algorithm:Algorithm):
        if moves_index < len(self.strategy):
            raise IndexError
            
        if moves_index > MAX_STEP:
            moves_index = MAX_STEP - moves_index

        self.strategy.extend([algorithm for _  in range(moves_index)])
        return self
        
    def __getitem__(self,move_index) -> Algorithm:
        return self.strategy[move_index]

    


_algoController = AlgoController()

