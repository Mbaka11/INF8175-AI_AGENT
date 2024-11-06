from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite
from seahorse.utils.custom_exceptions import MethodNotImplementedError

class MyPlayer(PlayerDivercite):
    """
    Player class for Divercite game that makes random moves.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "MyPlayer"):
        """
        Initialize the PlayerDivercite instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
            time_limit (float, optional): the time limit in (s)
        """
        super().__init__(piece_type, name)
        print("PIECE TYPE", piece_type)
        
    def max_value(self, state : GameState, depth : int, max_depth : int, alpha : float, beta : float) -> float:
        if depth == max_depth:
            score = state.scores[self.get_id()]
            return score, None
        
        v_prime = float('-inf')
        m_prime = None
        
        for action in state.generate_possible_light_actions():
            next_state = state.apply_action(action)
            v, _ = self.min_value(next_state, depth + 1, max_depth, alpha, beta)
            
            if v > v_prime:
                v_prime = v
                m_prime = action
                alpha = max(alpha, v_prime)
            
            if v_prime >= beta:
                return v_prime, m_prime
        
        return v_prime, m_prime
    
    def min_value(self, state: GameState, depth: int, max_depth: int, alpha: float, beta: float) -> float:
        if depth == max_depth:
            score = state.scores[self.get_id()]
            return score, None
        
        v_prime = float('inf')
        m_prime = None
        
        for action in state.generate_possible_light_actions():
            next_state = state.apply_action(action)
            v, _ = self.max_value(next_state, depth + 1, max_depth, alpha, beta)
            
            if v < v_prime:
                v_prime = v
                m_prime = action
                beta = min(beta, v_prime)
            
            if v_prime <= alpha:
                return v_prime, m_prime
        
        return v_prime, m_prime
            
    def compute_action(self, current_state: GameState, remaining_time: int = 1e9, **kwargs) -> Action:
        """
        Use the minimax algorithm to choose the best action based on the heuristic evaluation of game states.

        Args:
            current_state (GameState): The current game state.

        Returns:
            Action: The best action as determined by minimax.
        """
        print("NEXT_PLAYER", current_state.next_player)
        print("PLAYERS", current_state.players)
    
        #TODO
        max_depth = 4
        
        _, best_action = self.max_value(current_state, 0, max_depth, float('-inf'), float('inf'))
        return best_action