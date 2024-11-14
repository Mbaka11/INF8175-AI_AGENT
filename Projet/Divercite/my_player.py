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

    def __init__(self, piece_type: str, name: str = "Cité des Dieux"):
        """
        Initialize the PlayerDivercite instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
            time_limit (float, optional): the time limit in (s)
        """
        super().__init__(piece_type, name)
        pointDiffHeuristic = PointDifferenceHeuristic()

        self._controller: StrategyController = StrategyController().add_strategy(
            OpeningMoveStrategy(True), 2).add_strategy(
                MinimaxTypeASearch(pointDiffHeuristic,4,LRUCache(1500)),)

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
        return self._controller.play_best()
