from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite
from seahorse.utils.custom_exceptions import MethodNotImplementedError

from src_2147174_2117902.definition import Algorithm, Strategy
from src_2147174_2117902.strategy_controller import *
from src_2147174_2117902.tools import Monitor


class MyPlayer(PlayerDivercite):
    """
    Player class for Divercite game that makes random moves.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "LCD_ZePequeno"):
        """
        Initialize the PlayerDivercite instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
            time_limit (float, optional): the time limit in (s)
        """
        super().__init__(piece_type, name)
        scoreHeuristic = ScoreHeuristic()
        piecesVarianceHeuristic = PiecesVarianceHeuristic()
        controlIndexHeuristic = ControlIndexHeuristic()
        diverciteHeuristic = DiverciteHeuristic()

        hybrid = scoreHeuristic*8 + controlIndexHeuristic + piecesVarianceHeuristic
        hybrid2 = scoreHeuristic*8 + diverciteHeuristic*4 + \
            piecesVarianceHeuristic*4 + controlIndexHeuristic*2
        hybrid3 = diverciteHeuristic*70 + scoreHeuristic*30
        print(hybrid3)
        

        self._controller: StrategyController = StrategyController().add_strategy(
            OpeningMoveStrategy(False), 2).add_strategy(
                # MinimaxTypeASearch(controlIndexHeuristic,4,LRUCache(2500),3)).add_strategy(
     
                MinimaxTypeASearch( diverciteHeuristic, 3, 4500), 12).add_strategy(
                MinimaxTypeASearch( diverciteHeuristic, 5, 4500), 3).add_strategy(

                #MinimaxHybridSearch(diverciteHeuristic,4500,4,typeA_heuristic=scoreHeuristic,cut_depth_activation=False),6).add_strategy(

                #MinimaxTypeASearch( hybrid3, 3, LRUCache(4500)), 12).add_strategy(
                MinimaxTypeASearch(diverciteHeuristic, 6, LRUCache(5000)),)

    @Monitor
    def compute_action(self, current_state: GameStateDivercite, remaining_time: int = 1e9, **kwargs) -> Action:
        """
        Use the minimax algorithm to choose the best action based on the heuristic evaluation of game states.

        Args:
            current_state (GameState): The current game state.

        Returns:
            Action: The best action as determined by minimax.
        """
        # TODO
        Strategy.set_current_state(current_state, remaining_time)
        return self._controller()
