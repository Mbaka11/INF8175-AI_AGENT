from .definition import *
from .mcts_algorithm import *
from .minimax_algorithm import *
from .opening_moves import *
from .constant import *
from .heuristic import *


class StrategyController:
    
    def __init__(self):
        self.strategies:list[Strategy] = []
        self.strategy_count = 0

    def __call__(self, *args, **kwds):
        return self.play_best(*args)

    def play_best(self):
        moves_index = Strategy.my_step
        strategy = self[moves_index]
        return strategy.search()
        
    def add_strategy(self,strategy:Strategy | type[Strategy],number_of_moves:int | None = None):
        # NOTE add **kwards if we want to another way to create a strategy
        try:
            if isinstance(strategy,type):
                strategy = strategy()
        except:
            raise KeyError('This Strategy needs args, define it before passing to the class')

        if number_of_moves == None or number_of_moves > MAX_MOVES- len(self.strategies):
            number_of_moves = MAX_MOVES - len(self.strategies)

        self.strategies.extend([strategy for _  in range(number_of_moves)])
        return self
        
    def __getitem__(self,move_index) -> Strategy:
        return self.strategies[move_index]
    
    def strategy_from_dict(self, strategy:dict[int,Strategy],clear=False):
        if clear:
            self.strategies.clear()

        for move_step,algo in strategy.items():
            self.add_strategy(move_step,algo)
    
    def to_json(self):
        return {}
############################################### PREDEFINED STRATEGY ##############################################

pointDiffHeuristic =  PointDifferenceHeuristic()

STRATEGY_CONTROLLER = StrategyController().add_strategy(OpeningMoveStrategy(False),2).add_strategy(MinimaxTypeASearch(pointDiffHeuristic,None,4,LFUCache(200)),7).add_strategy(MinimaxTypeASearch(pointDiffHeuristic,None,6,LFUCache(200)))
#print(strategyController.strategies)
#print(strategyController.strategies)
