from genericpath import samestat
import math
import random
from typing import Callable

from bg_player import BGPlayer
from seahorse.game.action import Action
from seahorse.game.game_state import GameState

class MyPlayerBG(BGPlayer):
    """
    A player class for Connect4 that selects moves randomly.
    """

    def __init__(self, piece_type: str, name: str = "bob", strategy="random") -> None:
        """
        Initializes a new instance of the MyPlayerConnect4 class.

        Args:
            piece_type (str): The type of the player's game piece.
            name (str): The name of the player.
        """
        super().__init__(piece_type, name)
        self.strategy = strategy


    def random_strategy(self, current_state: GameState) -> Action:
        possible_actions = current_state.get_possible_heavy_actions()
        return random.choice(list(possible_actions))
    
    def minimax_strategy(self, currentState: GameState):
        """
        Implements the minimax strategy for the player.

        Args:
            currentState (GameState): The current game state.
        """
        def max_value(state: GameState):
            #TODO: Implement the max_value function for the minimax algorithm.
            raise NotImplementedError("The max_value function is not implemented yet.")

        def min_value(state: GameState):
            #TODO: Implement the min_value function for the minimax algorithm.
            raise NotImplementedError("The min_value function is not implemented yet.")

        return max_value(currentState)[1]

    def alpha_beta_strategy(self, currentState: GameState):
        def max_value(state: GameState, alpha, beta):
            #TODO: Implement the max_value function for the alpha-beta pruning algorithm.
            raise NotImplementedError("The max_value function is not implemented yet.")

        def min_value(state: GameState, alpha, beta):
            #TODO: Implement the min_value function for the alpha-beta pruning algorithm.
            raise NotImplementedError("The min_value function is not implemented yet.")
        
        return max_value(currentState, -math.inf, math.inf)[1]
    
    def halpha_beta_strategy(self, currentState: GameState, heuristic : Callable):

        def max_value(state: GameState, alpha, beta, depth):
            #TODO: Implement the max_value function for the alpha-beta pruning algorithm with heuristic.
            raise NotImplementedError("The max_value function is not implemented yet.")
        
        def min_value(state: GameState, alpha, beta, depth):
            #TODO: Implement the min_value function for the alpha-beta pruning algorithm with heuristic.
            raise NotImplementedError("The min_value function is not implemented yet.")
        
        return max_value(currentState, -math.inf, math.inf, 6)[1]
    
    def naive_heuristic(self, state: GameState):
        return 0 if not state.is_done() else state.get_player_score(self)
    
    def your_heuristic(self, state: GameState):
        #TODO: Implement your heuristic function.
        return 0
    

    
    def compute_action(self, current_state: GameState, **kwargs) -> Action:
        """
        Implements the logic of the player according to the strategy.

        Args:
            current_state (GameState): The current game state.
            **kwargs: Additional keyword arguments.

        """

        if self.strategy == "random":
            return self.random_strategy(current_state)
        
        elif self.strategy == "minimax":
            return self.minimax_strategy(current_state)
        
        elif self.strategy == "alphabeta":
            return self.alpha_beta_strategy(current_state)
        
        elif self.strategy == "h_alphabeta":
            return self.halpha_beta_strategy(current_state, heuristic=self.naive_heuristic)
        
        elif self.strategy == "your_player":
            return self.halpha_beta_strategy(current_state, heuristic=self.your_heuristic)
        else:
            raise ValueError("Invalid strategy")

        
