from ._strategy import Strategy, TestRandomAlgorithm
from .opening_moves import OpeningMovesStrategy
from .constant import *


class StrategyController:
    
    def __init__(self):
        self.strategies:list[Strategy] = []
        self.strategy_count = 0

    def __call__(self, *args, **kwds):
        return self.play_best(*args)

    def play_best(self, moves_index:int):
        strategy = self[moves_index]
        return strategy.search()
        
    def add_strategy(self, moves_index:int,algorithm:Strategy):
        if moves_index < len(self.strategies):
            raise IndexError
            
        if moves_index > MAX_MOVES:
            moves_index = MAX_MOVES - moves_index

        self.strategies.extend([algorithm for _  in range(moves_index)])
        return self
        
    def __getitem__(self,move_index) -> Strategy:
        return self.strategies[move_index]
    
    def strategy_from_dict(self, strategy:dict[int,Strategy],clear=False):
        if clear:
            self.strategies.clear()

        for move_step,algo in strategy.items():
            self.add_strategy(move_step,algo)

strategyController = StrategyController().add_strategy(1,OpeningMovesStrategy(False)).add_strategy(19,TestRandomAlgorithm())
#print(strategyController.strategies)
