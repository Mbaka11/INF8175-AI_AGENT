from src_2147174_2117902.tools import Monitor
from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from board_divercite import BoardDivercite
from tools import COLORS, CITY_KEY, RESOURCE_KEY, corner_ressource_position, B_PIECE, W_PIECE
from typing import Dict, Tuple, List, Set
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
    
    def get_placed_cities_by_player(self, state: GameStateDivercite, player: str) -> dict[tuple, str]:
        """
        Get all cities placed by a specific player on the board.

        Args:
            state (GameStateDivercite): The current game state.
            player (str): The symbol representing the player (e.g., 'W' for White or 'B' for Black).

        Returns:
            dict[tuple, str]: A dictionary mapping city positions (as tuples) to their respective piece types.
        """
        player_cities = {}
        board = state.get_rep().get_env() 

        # Iterate through the board to find cities belonging to the player
        for pos, piece in board.items():
            piece_type = piece.get_type()
            if piece_type[1] == CITY_KEY and piece_type[2] == player:
                player_cities[pos] = piece_type  # Store position as key and piece type as value
        
        return player_cities

    def get_total_pieces_on_board(self, state: GameStateDivercite) -> int:
        """
        Get the total number of placed pieces (non-empty) on the board.

        Args:
            state (GameStateDivercite): The current game state.

        Returns:
            int: The total number of pieces on the board.
        """
        board = state.get_rep().get_env()
        return len([piece for piece in board.values() if piece != 'EMPTY'])
    
    def get_colors_around_city(self, state: GameStateDivercite, city_pos: tuple[int, int]) -> list[str]:
        """
        Get the colors of all resources adjacent to a specified city.

        Args:
            state (GameStateDivercite): The current game state.
            city_pos (tuple[int, int]): The position of the city on the board.

        Returns:
            list[str]: A list of resource colors adjacent to the specified city.
        """
        adjacent_positions = state.get_neighbours(city_pos[0], city_pos[1])
        adjacent_colors = []

        # Collect colors of adjacent resources
        for direction, (piece, pos) in adjacent_positions.items():
            if piece != 'EMPTY' and hasattr(piece, 'get_type'):
                piece_type = piece.get_type()
                if piece_type[1] == RESOURCE_KEY:
                    adjacent_colors.append(piece_type[0])
        
        return adjacent_colors
           
    def get_missing_colors_for_divercite(self, current_colors: set[str]) -> str:
        """
        Identify a missing color needed to complete a divercité.

        Args:
            current_colors (set[str]): A set of colors already present around a city.

        Returns:
            Optional[str]: A missing color needed for divercité, or None if all colors are present.
        """
        missing_colors = COLORS - current_colors
        return missing_colors.pop() if missing_colors else None

    def get_cities_affected_by_ressource(self, state: GameStateDivercite, ressource_pos: Tuple[int, int]) -> Dict[Tuple[int, int], str]:
        """
        Identify all cities affected by a resource placed at a specific position.

        Args:
            state (GameStateDivercite): The current game state.
            ressource_pos (tuple[int, int]): The position of the resource on the board.

        Returns:
            dict[tuple[int, int], str]: A dictionary mapping city positions (tuples) to their respective piece types.
        """
        adjacent_positions = state.get_neighbours(ressource_pos[0], ressource_pos[1])
        adjacent_cities = {}
        
        # Collect cities affected by the resource
        for direction, (piece, pos) in adjacent_positions.items():
            if piece != 'EMPTY' and hasattr(piece, 'get_type'):
                piece_type = piece.get_type()
                if piece_type[1] == CITY_KEY:
                    adjacent_cities.update({pos: piece_type})
        
        return adjacent_cities

    def evaluate_resource_scarcity(self, state: GameStateDivercite) -> float:
        """
        Evaluate the scarcity of the player's remaining resources and penalize excessive usage.

        Args:
            state (GameStateDivercite): The current game state.

        Returns:
            float: A score penalizing resource scarcity. A lower score indicates more scarce or depleted resources.
        """
        # Constants
        DEPLETION_PENALTY = 150  # Penalty for completely depleting a resource color
        SCARCITY_MULTIPLIER = 100  # Penalty scaling for scarce resources
        
        # Get the player's remaining pieces
        player_pieces_left = state.players_pieces_left[self.get_id()]
        total_pieces = sum(player_pieces_left.values())

        score = 0
        # Penalize if a specific resource color is disproportionately used
        for piece, count in player_pieces_left.items():
            if count == 0:  # Resource depleted
                score -= DEPLETION_PENALTY  # Heavy penalty for completely depleting a color
            else:
                scarcity_ratio = count / total_pieces
                score -= (1 - scarcity_ratio) * SCARCITY_MULTIPLIER  # Penalize if resource is scarce

        return score

    def evaluate_ressource_placement(self, state: GameStateDivercite) -> float:
        """
        Evaluate the placement of resources based on their proximity to cities and strategic importance.

        Args:
            state (GameStateDivercite): The current game state.

        Returns:
            float: A score reflecting the quality of resource placement. Higher scores indicate better placements.
        """
        # Constants
        FRIENDLY_CITY_BONUS = 20
        OPPONENT_CITY_PENALTY = 25
        OPPONENT_ADVANTAGE_PENALTY = 75
        CORNER_OPPONENT_PENALTY = 250
        COLOR_MATCH_PENALTY = 30
        COMPLETE_DIVERCITE_PENALTY = 200
        NEARLY_COMPLETE_DIVERCITE_PENALTY = 100
        NO_ADJACENT_CITIES_PENALTY = 20
        
        score = 0
        board = state.get_rep().get_env()
        
        for pos, piece in board.items():
            piece_type = piece.get_type()
            if piece_type[1] == RESOURCE_KEY: # Skip non-resource pieces
                # Get cities affected by this resource
                adjacent_cities = self.get_cities_affected_by_ressource(state, pos)
                
                if adjacent_cities:
                    # Separate cities into friendly and opponent
                    opponent_cities = [city for city in adjacent_cities.values() if city[2] != self.piece_type]
                    friendly_cities = [city for city in adjacent_cities.values() if city[2] == self.piece_type]
                    friendly_city_count = len(friendly_cities)
                    opponent_city_count = len(opponent_cities)
                    
                    # Adjust score based on affected cities
                    score += FRIENDLY_CITY_BONUS  * friendly_city_count
                    score -= OPPONENT_CITY_PENALTY  * opponent_city_count
                    
                    if friendly_city_count == 0:
                        score -= OPPONENT_ADVANTAGE_PENALTY  * (opponent_city_count ** 2)
                    
                    if pos in corner_ressource_position and opponent_city_count > 0:
                        score -= CORNER_OPPONENT_PENALTY
                    
                    opponent_cities_dict = {city_pos: city_type for city_pos, city_type in adjacent_cities.items() if city_type[2] != self.piece_type}
                    for opponent_city_pos, opponent_city_type in opponent_cities_dict.items():
                        opponent_city_color = opponent_city_type[0]
                        piece_color = piece_type[0]
                        
                        # Penalize for matching colors with opponent cities
                        if opponent_city_color == piece_color:
                            score -= COLOR_MATCH_PENALTY * len([city for city in adjacent_cities.values() if city[0] == piece_color])
                        
                        adjacent_colors = self.get_colors_around_city(state, opponent_city_pos)
                        unique_colors = set(adjacent_colors)
                        
                        # Penalize for nearly complete opponent divercité
                        if len(unique_colors) == 4 : 
                            score -= COMPLETE_DIVERCITE_PENALTY
                        # Penalize for nearly complete oponnent divercité
                        elif len(unique_colors) == 3 and len(adjacent_colors) == 3:
                            score -= NEARLY_COMPLETE_DIVERCITE_PENALTY
                    
                elif not adjacent_cities:
                    score -= NO_ADJACENT_CITIES_PENALTY
                
        return score
    
    def evaluate_city_placement(self, state: GameStateDivercite) -> float:
        """
        Evaluate the placement of cities based on their proximity to resources and strategic value.

        Args:
            state (GameStateDivercite): The current game state.

        Returns:
            float: A score reflecting the quality of city placements. Higher scores indicate better placements.
        """
        # Constants
        FULL_DIVERCITE_BONUS = 200
        INEFFICIENT_RESOURCES_PENALTY = 50
        SINGLE_COLOR_BONUS = 20
        MULTI_COLOR_BONUS = 30
        ISOLATED_CITY_PENALTY = 100
        MIN_RESOURCES_THRESHOLD = 5
        
        score = 0
        board = state.get_rep().get_env()
        
        for pos, piece in board.items():
            piece_type = piece.get_type()
            if piece_type[1] == CITY_KEY: # Skip non-city pieces
                # Analyze adjacent resources
                adjacent_colors = self.get_colors_around_city(state, pos)
                adjacent_resource_count = len(adjacent_colors)
                unique_colors = set(adjacent_colors)
                city_color = piece_type[0]
                
                # Case 1: Full divercité (4 unique colors)
                if len(unique_colors) == 4:
                    score += FULL_DIVERCITE_BONUS
                    
                # Case 2: Inefficient resource placement (2 unique colors, not matching city color)
                elif len(unique_colors) == 2 and adjacent_resource_count > 2 and city_color not in unique_colors:
                    score -= INEFFICIENT_RESOURCES_PENALTY

                # Case 3: Single color matches city color
                elif len(unique_colors) == 1 and city_color in unique_colors:
                    score += SINGLE_COLOR_BONUS * adjacent_resource_count

                # Case 4: Multiple colors with city color included
                elif city_color in unique_colors: 
                    score += MULTI_COLOR_BONUS * len(unique_colors)
                
                # Case 5: Isolated city with no adjacent resources (after early game)
                elif adjacent_resource_count == 0 and self.get_total_pieces_on_board(state) > MIN_RESOURCES_THRESHOLD:
                    score -= ISOLATED_CITY_PENALTY
                    
        return score
        
    def calculate_blocking_score(self, state: GameStateDivercite) -> float:
        """
        Calculate a score for blocking opponent cities from achieving DiverCité.

        Args:
            state (GameStateDivercite): The current game state.

        Returns:
            float: A score reflecting the blocking effectiveness. Higher scores indicate better blocking.
        """
        # Constants
        BLOCKING_BONUS_FULL = 200
        BLOCKING_BONUS_PARTIAL = 100
        BLOCKING_PENALTY = 50
        
        score = 0
        opponent_symbol = B_PIECE if self.piece_type == W_PIECE else W_PIECE
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
                # Count occurrences of each color
                color_counts = {color: adjacent_colors.count(color) for color in unique_colors}
                
                # Identify if there's a repeated color that makes DiverCité impossible
                repeated_colors = [color for color, count in color_counts.items() if count > 1]
                
                if len(repeated_colors) > 0:
                    # DiverCité impossible due to repeated colors
                    continue  # Skip this city as no threat exists
                
                ennemy_color_ressource_left = state.players_pieces_left[self.next_player.get_id()]
                keys_to_remove = [key for key, value in ennemy_color_ressource_left.items() if (value == 0 and key[1] == RESOURCE_KEY) or key[1] == CITY_KEY]
                for key in keys_to_remove:
                    ennemy_color_ressource_left.pop(key)
                
                missing_color = self.get_missing_colors_for_divercite(unique_colors)
                
                if missing_color + RESOURCE_KEY in ennemy_color_ressource_left:
                    score += BLOCKING_BONUS_FULL
                
            elif len(unique_colors) == 2 and len(adjacent_colors) == 4 and adjacent_colors.count(blocking_color) == 1:
                # Check for blocking potential with only 2 resources
                # Ensure no color is repeated that prevents DiverCité
                color_counts = {color: adjacent_colors.count(color) for color in unique_colors}
                repeated_colors = [color for color, count in color_counts.items() if count > 1]
                
                if len(repeated_colors) == 0:
                    score += BLOCKING_BONUS_PARTIAL 
                    
            elif len(unique_colors) == 3 and len(adjacent_colors) == 3 and adjacent_colors.count(blocking_color) == 1:
                # Check for blocking potential with only 3 resources
                # Ensure no color is repeated that prevents DiverCité
                color_counts = {color: adjacent_colors.count(color) for color in unique_colors}
                repeated_colors = [color for color, count in color_counts.items() if count > 1]
                
                if len(repeated_colors) == 0:
                    # DiverCité is still theoretically possible, valid blocking
                    score -= BLOCKING_PENALTY
                    
        return score
         
    def calculate_divercite_score(self, state: GameStateDivercite) -> float:
        """
        Calculate a score for the player's cities based on their progress towards DiverCité.

        Args:
            state (GameStateDivercite): The current game state.

        Returns:
            float: A score reflecting the progress of the player's cities towards DiverCité.
        """
        # Constants for scoring
        FULL_DIVERCITE_SCORE = 600
        SINGLE_COLOR_SCORE = 100
        RESOURCE_BONUS = 15
        CLOSE_TO_DIVERCITE_BONUS = 60
        OPPONENT_ADVANTAGE_PENALTY = 100
        INEFFICIENT_PLACEMENT_PENALTY = 50
        DIVERCIET_NOT_POSSIBLE_PENALTY = 50
        LACK_OF_RESOURCES_PENALTY = 10
        
        score = 0
        player_symbol = self.piece_type
        player_cities = self.get_placed_cities_by_player(state, player_symbol)

        for city_pos in player_cities.keys():
            adjacent_colors = self.get_colors_around_city(state, city_pos)
            unique_colors = set(adjacent_colors)
            city_color = player_cities[city_pos][0]
            
            # Case 1: Full DiverCité (4 unique colors, 4 adjacent resources)
            if len(unique_colors) == 4 and len(adjacent_colors) == 4:
                score += FULL_DIVERCITE_SCORE  # Full divercité, highest score

            # Case 2: Single color surrounds city
            elif len(unique_colors) == 1 and city_color in unique_colors:
                if len(adjacent_colors) == 4:
                    score += SINGLE_COLOR_SCORE
                else:
                    score += RESOURCE_BONUS * len(adjacent_colors) 
                    
            # Case 3: Close to DiverCité (3 unique colors, 3 resources)
            elif len(unique_colors) == 3 and len(adjacent_colors) == 3 and city_color in unique_colors:
                missing_color = self.get_missing_colors_for_divercite(unique_colors)
                empty_positions = [
                            pos for _, (piece, pos) in state.get_neighbours(city_pos[0], city_pos[1]).items() if piece == 'EMPTY'
                        ]
                if empty_positions:
                    for empty_pos in empty_positions:
                        adjacent_cities = self.get_cities_affected_by_ressource(state, empty_pos)
                        opponent_cities = [city for city in adjacent_cities.values() if city[2] != self.piece_type]
                        opponent_cities_colors = [city[0] for city in opponent_cities]
                        
                        color_ressources_left = state.players_pieces_left[self.get_id()]
                        # Collect keys to remove in a separate list+
                        keys_to_remove = [key for key, value in color_ressources_left.items() if (value == 0 and key[1] == RESOURCE_KEY) or key[1] == CITY_KEY]

                        # Remove the keys after the iteration
                        for key in keys_to_remove:
                            color_ressources_left.pop(key)
                        
                        if missing_color in color_ressources_left and opponent_cities:
                            score -= OPPONENT_ADVANTAGE_PENALTY * len(opponent_cities)
                            
                        elif missing_color + RESOURCE_KEY in color_ressources_left :
                            score += CLOSE_TO_DIVERCITE_BONUS
                            
                        else:
                            score -= OPPONENT_ADVANTAGE_PENALTY
            
            # Case 4: Two colors with two resources    
            elif len(unique_colors) == 2 and len(adjacent_colors) == 2 and city_color in unique_colors:
                missing_color = self.get_missing_colors_for_divercite(unique_colors)
                color_ressources_left = state.players_pieces_left[self.get_id()]
                keys_to_remove = [key for key, value in color_ressources_left.items() if (value == 0 and key[1] == RESOURCE_KEY) or key[1] == CITY_KEY]
                for key in keys_to_remove:
                    color_ressources_left.pop(key)
                
                if missing_color in color_ressources_left:
                    score += INEFFICIENT_PLACEMENT_PENALTY
            
            # Case 5: Inefficient placements or blocked DiverCité    
            elif len(unique_colors) == 3 and len(adjacent_colors) == 4 and adjacent_colors.count(city_color) < 3:
                score -= INEFFICIENT_PLACEMENT_PENALTY  # Penalize since divercité is not possible
    
            elif len(unique_colors) == 2 and len(adjacent_colors) == 4 and city_color not in unique_colors:
                score -= INEFFICIENT_PLACEMENT_PENALTY  # Penalize lightly for inefficiency
            
            elif len(unique_colors) == 2 and len(adjacent_colors) == 3 and adjacent_colors.count(city_color) < 2:
                score -= OPPONENT_ADVANTAGE_PENALTY
            
            # Case 6: City with no matching resources
            elif city_color not in unique_colors and unique_colors:
                score -= DIVERCIET_NOT_POSSIBLE_PENALTY  # Penalize for placing a city with no adjacent resources of the same color
            
            # Default penalty for poor placement    
            else :
                score -= LACK_OF_RESOURCES_PENALTY
                
        return score
    
    def heuristic_evaluation(self, state: GameStateDivercite) -> float:
        """
        Evaluate the current game state using a heuristic that combines multiple scores.

        Args:
            state (GameStateDivercite): The current game state.

        Returns:
            float: A total heuristic score representing the favorability of the game state.
        """
        # Compute individual scores
        score_divercite = self.calculate_divercite_score(state)
        score_blocking = self.calculate_blocking_score(state)
        player_actual_score = state.scores[self.get_id()]
        score_resource_scarcity = self.evaluate_resource_scarcity(state)
        score_ressource_placement = self.evaluate_ressource_placement(state)
        city_placement_score = self.evaluate_city_placement(state)

        # Compute game progress (percentage of pieces placed)
        progress = ( self.get_total_pieces_on_board(state) / 42 ) * 100

        # Adjust weights dynamically    
        w_divercite = 1.0 if progress < 80 else 0.5
        w_blocking  = 1
        w_ressource_scarcity = 0.8 if progress < 40 else 0.3

        # Combine scores with weights
        total_score = (
            w_divercite * score_divercite +
            w_blocking * score_blocking +
            score_ressource_placement +
            player_actual_score +
            city_placement_score +
            w_ressource_scarcity * score_resource_scarcity
        )

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
    @Monitor 
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