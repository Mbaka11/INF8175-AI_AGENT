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

    def get_total_pieces_on_board(self, state: GameState) -> int:
        board = state.get_rep().get_env()
        return len([piece for piece in board.values() if piece != 'EMPTY'])
    
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
        all_colors = {'R', 'G', 'B', 'Y'}
        missing_colors = all_colors - current_colors
        return missing_colors.pop() if missing_colors else None

    def get_cities_affected_by_ressource(self, state: GameState, ressource_pos: tuple) -> dict:
        adjacent_positions = state.get_neighbours(ressource_pos[0], ressource_pos[1])
        adjacent_cities = {}
        
        for direction, (piece, pos) in adjacent_positions.items():
            if piece != 'EMPTY' and hasattr(piece, 'get_type'):
                piece_type = piece.get_type()
                if piece_type[1] == 'C':
                    adjacent_cities.update({pos: piece_type})
        
        return adjacent_cities

    def evaluate_ressource_placement(self, state: GameState) -> float:
        # Heuristic to boost the placement of ressources next to cities
        score = 0
        board = state.get_rep().get_env()
        
        for pos, piece in board.items():
            piece_type = piece.get_type()
            if piece_type[1] == 'R':
                adjacent_cities = self.get_cities_affected_by_ressource(state, pos)
                if adjacent_cities:
                    friendly_city_count = len([city for city in adjacent_cities.values() if city[2] == self.piece_type])
                    opponent_city_count = len([city for city in adjacent_cities.values() if city[2] != self.piece_type])
                    
                    # Reward placements near friendly cities but penalize or ignore placements near opponent cities
                    score += 15 * friendly_city_count - 20 * opponent_city_count
                
        return score
        
    def calculate_blocking_score(self, state: GameState) -> float:
        # Heuristic to boost the blocking of cities with 3 different colors around them
        score = 0
        opponent_symbol = 'B' if self.piece_type == 'W' else 'W'
        opponent_cities = self.get_placed_cities_by_player(state, opponent_symbol)
        
        for city_pos in opponent_cities.keys():
            adjacent_colors = self.get_colors_around_city(state, city_pos)
            unique_colors = set(adjacent_colors)
            city_color = opponent_cities[city_pos][0]
            blocking_color = next(
                (color for color in unique_colors if color != city_color),
                None
            )
            
            if len(unique_colors) == 3 and len(adjacent_colors) == 4 and adjacent_colors.count(blocking_color) == 2:
                score += 125
            elif len(unique_colors) == 2 and len(adjacent_colors) == 3 and adjacent_colors.count(blocking_color) == 1:
                score += 50
        return score
         
    def calculate_divercite_score(self, state: GameState) -> float:
        score = 0
        player_symbol = self.piece_type
        player_cities = self.get_placed_cities_by_player(state, player_symbol)

        for city_pos in player_cities.keys():
            adjacent_colors = self.get_colors_around_city(state, city_pos)
            unique_colors = set(adjacent_colors)\
            
            # Case 1: Full divercité (4 unique colors + 4 ressources => 5 points)
            if len(unique_colors) == 4:
                score += 200
            # Case 2: Full unique color ( 1 unique color + 4 ressources => 4 points)
            elif len(unique_colors) == 1 and len(adjacent_colors) == 4:
                score += 125
            elif len(unique_colors) == 3 and len(adjacent_colors) == 3:
                missing_color = self.get_missing_colors_for_divercite(unique_colors)
                if missing_color in {piece[0] for piece in state.players_pieces_left[state.next_player.get_id()]}:
                    score += 50
            elif len(unique_colors) == 2 and len(adjacent_colors) == 2 :
                score += 25
    
        return score
    
    def heuristic_evaluation(self, state: GameState) -> float:
        score_divercite = self.calculate_divercite_score(state)
        score_bloquage = self.calculate_blocking_score(state)
        player_actual_score = state.scores[self.get_id()]

        progress = ( self.get_total_pieces_on_board(state) / 42 ) * 100

        # Adjust weights dynamically    
        w_divercite = 1.0 if progress < 50 else 0.5
        w_bloquage = 0.8 if progress < 50 else 1.5

        score_divercite = self.calculate_divercite_score(state)
        score_bloquage = self.calculate_blocking_score(state)
        score_ressource_placement = self.evaluate_ressource_placement(state)
        
        total_score = (
            w_divercite * score_divercite +
            w_bloquage * score_bloquage +
            score_ressource_placement +
            player_actual_score
        )
        
        print(f"Divercite score: {score_divercite}, Blocking score: {score_bloquage}, "
            f"Ressource placement score: {score_ressource_placement},")
        print(f"Total score: {total_score}")

        return total_score
        
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