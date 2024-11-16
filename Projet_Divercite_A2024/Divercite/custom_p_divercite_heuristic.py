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

    def evaluate_resource_scarcity(self, state: GameState) -> float:
        """
        Penalize excessive use of scarce resources.
        """
        score = 0
        player_pieces_left = state.players_pieces_left[self.get_id()]
        total_pieces = sum(player_pieces_left.values())

        # Penalize if a specific resource color is disproportionately used
        for piece, count in player_pieces_left.items():
            color = piece[0]  # Extract the color
            if count == 0:  # Resource depleted
                score -= 90  # Heavy penalty for completely depleting a color
            else:
                scarcity_ratio = count / total_pieces
                score -= (1 - scarcity_ratio) * 20  # Penalize if resource is scarce

        return score

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
                    
                    # Reward placements benefiting friendly cities
                    score += 50 * friendly_city_count
                    # Penalize placements helping opponent cities
                    score -= 100 * opponent_city_count
                
                    opponent_cities = [city for city in adjacent_cities.values() if city[2] != self.piece_type]
                    for city in opponent_cities:
                        city_color = city[0]
                        if city_color == piece_type[0]:
                            score -= 100
                        adjacent_colors = self.get_colors_around_city(state, pos)
                        adjacent_resource_count = len(adjacent_colors)
                        unique_colors = set(adjacent_colors)
                        if len(unique_colors) == 4:
                            score -= 300
                        
                elif not adjacent_cities:
                    score -= 50
                
        return score
    
    def evaluate_city_placement(self, state: GameState) -> float:
        # Heuristic to boost the placement of cities near resources
        score = 0
        board = state.get_rep().get_env()
        
        for pos, piece in board.items():
            piece_type = piece.get_type()
            if piece_type[1] == 'C':
                adjacent_colors = self.get_colors_around_city(state, pos)
                adjacent_resource_count = len(adjacent_colors)
                unique_colors = set(adjacent_colors)
                city_color = piece_type[0]
                
                if len(unique_colors) == 1 :
                    score += 10 * adjacent_resource_count
                elif city_color not in unique_colors and unique_colors:
                    score -= 150
                elif len(unique_colors) == 4:
                    score += 200
                    
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
                score += 200
            elif len(unique_colors) == 2 and len(adjacent_colors) == 3 and adjacent_colors.count(blocking_color) == 1:
                score += 50
        return score
         
    def calculate_divercite_score(self, state: GameState) -> float:
        score = 0
        player_symbol = self.piece_type
        player_cities = self.get_placed_cities_by_player(state, player_symbol)

        for city_pos in player_cities.keys():
            adjacent_colors = self.get_colors_around_city(state, city_pos)
            unique_colors = set(adjacent_colors)
            city_color = player_cities[city_pos][0]
            
            # Case 1: Full divercité (4 unique colors + 4 resources => 5 points)
            if len(unique_colors) == 4 and len(adjacent_colors) == 4:
                score += 500  # Full divercité, highest score

            # Case 2: Full same color (1 unique color + 4 resources => 4 points)
            elif len(unique_colors) == 1 and len(adjacent_colors) == 4 and city_color in unique_colors:
                score += 125  # Same color fully surrounding the city
            
            elif len(unique_colors) == 1 and len(adjacent_colors) == 3 and city_color in unique_colors:
                score += 30
                
            elif len(unique_colors) == 1 and len(adjacent_colors) == 2 and city_color in unique_colors:
                score += 15
                
            # Case 3: 3 unique colors + 3 resources => one step toward divercité
            elif len(unique_colors) == 3 and len(adjacent_colors) == 3 and city_color in unique_colors:
                missing_color = self.get_missing_colors_for_divercite(unique_colors)
                # Check if the missing color is available in the player's remaining pieces
                if missing_color in {piece[0] for piece in state.players_pieces_left[self.get_id()]}:
                    score += 50  # Prioritize this city as it is close to divercité
                
            # Case 4: 2 unique colors + 2 resources => early progress
            elif len(unique_colors) == 2 and len(adjacent_colors) == 2 and city_color in unique_colors:
                score += 15  # Moderate reward for potential progress
                
            # Case 5: 1 unique color + 1 resource => initial placement
            elif len(unique_colors) == 1 and len(adjacent_colors) == 1 and city_color in unique_colors:
                score += 10  # Minimal progress, lowest reward
                
            # Case 6: 3 unique colors + 4 resources => incomplete divercité
            elif len(unique_colors) == 3 and len(adjacent_colors) == 4:
                missing_color = self.get_missing_colors_for_divercite(unique_colors)
                if not missing_color:
                    score -= 20  # Penalize since divercité is not possible
    
            # Case 7: 2 unique colors + 4 resources (Locked city)
            elif len(unique_colors) == 2 and len(adjacent_colors) == 4:
                score -= 20  # Penalize lightly for inefficiency
            
            elif city_color not in unique_colors and unique_colors:
                score -= 50  # Penalize for placing a city with no adjacent resources of the same color
                
            else :
                score -= 30
                
        return score
    
    def heuristic_evaluation(self, state: GameState) -> float:
        score_divercite = self.calculate_divercite_score(state)
        score_bloquage = self.calculate_blocking_score(state)
        player_actual_score = state.scores[self.get_id()]
        score_resource_scarcity = self.evaluate_resource_scarcity(state)

        progress = ( self.get_total_pieces_on_board(state) / 42 ) * 100

        # Adjust weights dynamically    
        # w_divercite = 1.0 if progress < 50 else 0.5
        # w_bloquage = 0.8 if progress < 50 else 1.5
        w_divercite = 1
        w_bloquage = 1
        w_ressource_scacity = 1 if progress < 40 else 0.3

        score_divercite = self.calculate_divercite_score(state)
        score_bloquage = self.calculate_blocking_score(state)
        score_ressource_placement = self.evaluate_ressource_placement(state)
        city_placement_score = self.evaluate_city_placement(state)
        
        total_score = (
            w_divercite * score_divercite +
            w_bloquage * score_bloquage +
            score_ressource_placement +
            player_actual_score +
            city_placement_score +
            w_ressource_scacity * score_resource_scarcity
        )
        
        print(f"Divercite score: {score_divercite}, Blocking score: {score_bloquage}, "
            f"Ressource placement score: {score_ressource_placement}, City placement score: {city_placement_score}")
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