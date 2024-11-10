from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from board_divercite import BoardDivercite

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
    
    def get_placed_cities_by_player(self, state: GameState, player: str) -> dict:
        player_cities = {}
        board = state.get_rep().get_env() 
        
        for pos, piece in board.items():
            piece_type = piece.get_type()
            if piece_type[1] == 'C' and piece_type[2] == player:
                player_cities[pos] = piece_type  # Store position as key and piece type as value
                # print(f"Player {player} has a city at {pos} of type {piece_type}")
        
        return player_cities
    
    def get_colors_around_city(self, state: GameState, city_pos: tuple) -> list:
        adjacent_positions = state.get_neighbours(city_pos[0], city_pos[1])
        adjacent_colors = []
        for direction, (piece, pos) in adjacent_positions.items():
            if piece != 'EMPTY' and hasattr(piece, 'get_type'):
                piece_type = piece.get_type()
                if piece_type[1] == 'R':
                    adjacent_colors.append(piece_type[0])
        
        return adjacent_colors
           
    def get_missing_colors_for_divercite(self, current_colors: set) -> str:
        all_colors = {'R', 'G', 'B'}
        missing_colors = all_colors - current_colors
        return missing_colors.pop() if missing_colors else None
         
    def divercite_heuristic(self, state: GameState) -> float:
        # Heuristic to boost the completion of own cities with 3 different colors around them
        score = 0
        player_symbol = self.piece_type
        player_cities = self.get_placed_cities_by_player(state, player_symbol)

        for city_pos in player_cities.keys():
            adjacent_colors = self.get_colors_around_city(state, city_pos)
            unique_colors = set(adjacent_colors)\
            
            # Case 1: Full divercité (4 unique colors + 4 ressources => 5 points)
            if len(unique_colors) == 4:
                score += 100
            # Case 2: Full unique color ( 1 unique color + 4 ressources => 4 points)
            elif len(unique_colors) == 1 and len(adjacent_colors) == 4:
                score += 75
            # Case 3: 3 unique colors + 3 ressources => 1 point (NEED TO SEE IF THE SAME COLOR IS THERE OR BOOST THIS ONE) and moving towards divercité
            elif len(unique_colors) == 3 and len(adjacent_colors) == 3:
                missing_color = self.get_missing_colors_for_divercite(unique_colors)
                print(f"PLayer piueces left: {state.players_pieces_left[state.next_player.get_id()]}")
                if missing_color in state.players_pieces_left[state.next_player.get_id()] :
                    score += 50
            # Case 4: 2 unique colors + 2 ressources =>  point and moving towards divercité
            elif len(unique_colors) == 2 and len(adjacent_colors) == 2 :
                score += 25
    
        return score
    
    def heuristic_evaluation(self, state: GameState) -> float:
        player_actual_score = state.scores[self.get_id()]
        player_pieces_left = state.players_pieces_left[self.get_id()]
        divercite_heuristic_score = self.divercite_heuristic(state)
        
        # return player_actual_score + player_pieces_left + divercite_heuristic_score
        return divercite_heuristic_score + player_actual_score
        
    def max_value(self, state : GameState, depth : int, max_depth : int, alpha : float, beta : float) -> float:
        if depth == max_depth:
            score = self.heuristic_evaluation(state)
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
            score = self.heuristic_evaluation(state)
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

        #TODO
        max_depth = 2
        
        _, best_action = self.max_value(current_state, 0, max_depth, float('-inf'), float('inf'))
        return best_action