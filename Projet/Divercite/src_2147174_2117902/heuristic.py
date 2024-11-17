from typing import Any
from game_state_divercite import GameStateDivercite
from .definition import AlgorithmHeuristic, Heuristic, ARGS_KEYS
from .constant import *
from .helper import *
import numpy as np
from random import random


class PointDifferenceHeuristic(AlgorithmHeuristic):

    def __init__(self):
        super().__init__(-35, 35, L=6)

    def _evaluation(self, current_state, **kwargs):
        my_state_score = current_state.get_scores()[kwargs['my_id']]
        opponent_state_score = current_state.get_scores()[
            kwargs['opponent_id']]

        my_current_score = kwargs['my_score']
        opponent_current_score = kwargs['opponent_score']
        # BUG Might want to revisit the way we quantify this heuristic and remove the cross diff
        return self._maximize_score_diff(my_current_score, opponent_current_score, my_state_score, opponent_state_score)

class ControlIndexHeuristic(AlgorithmHeuristic):

    def __init__(self,ctrl_weight=.35,dist_weight=.65,):
        super().__init__(0, 900,L=11)
        self.ctrl_weight = ctrl_weight
        self.dist_weight= dist_weight
        self.total_weight = ctrl_weight + dist_weight

    def _evaluation(self, current_state, **kwargs):
        my_piece_type = kwargs['my_piece_type']
        original_env: dict = kwargs['current_env']
        opp_piece_type = kwargs['opponent_piece_type']
        state_env = current_state.rep.env

        (my_state_moves, my_ic_state), (opp_state_moves, opp_ic_state) = self._filter_moves_control_index(
            current_state.rep.env, my_piece_type)
        (my_current_moves, my_current_ic), (opp_current_moves, opp_current_ic) = self._filter_moves_control_index(
            original_env, my_piece_type)

        control_index = self._maximize_score_diff(
            my_current_ic, opp_current_ic, my_ic_state, opp_ic_state)

        my_current_dist = self._compute_neighborhood_distances(
            my_piece_type, my_current_moves, original_env)
        opp_current_dist = self._compute_neighborhood_distances(
            opp_piece_type, opp_current_moves, original_env)

        my_state_dist = self._compute_neighborhood_distances(
            my_piece_type, my_state_moves, state_env)
        opp_state_dist = self._compute_neighborhood_distances(
            opp_piece_type, opp_state_moves, state_env)

        dist_index = self._maximize_score_diff(
            my_current_dist, opp_current_dist, my_state_dist, opp_state_dist)

        control_index =self._compute_control_index(control_index)
        dist_index = self._compute_distance_index(dist_index)

        return (control_index*self.ctrl_weight + dist_index*self.dist_weight)/self.total_weight  #NOTE we can add weight it depends on which is more important


    def _compute_neighborhood_distances(self, pieces_type: str, added_moves: dict[tuple, str], state_env: dict[tuple, str]):
        score = 0
        index = 0
        for move_pos, pieces in added_moves.items():

            m_x, m_y = move_pos
            c, _ = pieces

            for pos in horizontal_vertical_compute + diagonal_compute:
                index += 1
                in_horizontal = index <= 4

                i, j = pos

                computed_pos = m_x+i, m_y + j
                if not is_in_board(computed_pos):
                    continue
                if not computed_pos in state_env:  # check neighbours
                    continue
                p_color, _, p_owner = state_env[computed_pos].piece_type

                if c == p_color and pieces_type == p_owner:  # same color and same ownership
                    score += (10 if in_horizontal else 15)
                
                elif c != p_color and pieces_type == p_owner:  # diff color but same ownership
                    score += (15 if in_horizontal else 10)

                elif c == p_color and pieces_type != p_owner:  # same color but diff ownership
                    score += (25 if in_horizontal else 20)      
                else:                                           # different ownership and diff_color
                    score += (35 if in_horizontal else 30)

        return score

    def _filter_moves_control_index(self, env: dict[tuple, Any], my_piece_type: str):
        my_moves = {}
        opp_moves = {}
        my_ic = 0
        opp_ic = 0

        for pos, piece in env.items():
            piece_type = piece.piece_type
            if is_ressource(piece_type):
                continue
            if piece_type.endswith(my_piece_type):
                my_moves[pos] = piece_type[:2]
                my_ic += control_index(pos)
            else:
                opp_moves[pos] = piece_type[:2]
                opp_ic += control_index(pos)

        return (my_moves, my_ic), (opp_moves, opp_ic)

    def _compute_control_index(self,x:float):
        return self._range_scaling(x,3,52)
    
    def _compute_distance_index(self,x:float):
        return self._range_scaling(x,100,700)

    def normalize(self, x):
        return x

class PiecesVarianceHeuristic(AlgorithmHeuristic):

    def __init__(self, city_weight=.7, ress_weight=.3):
        super().__init__(-160, 160, L=4.3) # URGENT-TODO Recheck the scaling depends on minimize or maximize
        self.city_weight = city_weight
        self.ress_weight = ress_weight

    def _evaluation(self, current_state, **kwargs):
        opponent_pieces = current_state.players_pieces_left[kwargs['opponent_id']]
        my_pieces = current_state.players_pieces_left[kwargs['my_id']]
        #####
        my_state_var = self._pieces_var(my_pieces)
        opp_state_var = self._pieces_var(opponent_pieces)

        return  opp_state_var-my_state_var # URGENT-TODO Compute potential
        #return -my_state_var
        
    def _pieces_var(self, pieces: dict[str, int]):
        city_val = np.array([pieces[cn] for cn in CityNames._member_names_])
        ress_val = np.array([pieces[rn] for rn in RessourcesNames._member_names_])
        
        is_tuning = ress_val.sum() > city_val.sum()
        if is_tuning:
            city_val +=1

        score_city = float(np.var(city_val))*100
        score_ress = float(np.var(ress_val))*100
        city_penalty = 30 if is_tuning else 20
        ress_penalty = 20 if is_tuning else 30

        score_city = city_penalty if score_city ==0 else score_city
        score_ress = ress_penalty if score_ress ==0 else score_ress

        return score_city + score_ress

        ##################################
        # city_val = np.var(city_val)
        # ress_val = np.var(ress_val)*1.05

        # ress_val = 0.5 if ress_val == 0 else ress_val
        # return -min(city_val, ress_val)
        # return float(city_val*self.city_weight+ ress_val*self.ress_weight)/self._h_tot_weight
        # return float(city_val+ress_val)
        ##########################
        # pieces_vectors = (city_val*self.city_weight + ress_val*self.ress_weight)/self._h_tot_weight
        # return float(np.var(pieces_vectors)*100)
        # 33

    @property
    def _h_tot_weight(self):
        return self.city_weight+self.ress_weight

class DiverciteHeuristic(AlgorithmHeuristic):
    def __init__(self, min_value, max_value,L=...):
        super().__init__(min_value, max_value, L)

    
    def get_placed_cities_by_player(self, state: GameStateDivercite, player: str) -> dict:
        player_cities = {}
        board = state.get_rep().get_env() 
        
        for pos, piece in board.items():
            piece_type = piece.get_type()
            if piece_type[1] == 'C' and piece_type[2] == player:
                player_cities[pos] = piece_type  # Store position as key and piece type as value
                # print(f"Player {player} has a city at {pos} of type {piece_type}")
        
        return player_cities

    def get_total_pieces_on_board(self, state: GameStateDivercite) -> int:
        board = state.get_rep().get_env()
        return len([piece for piece in board.values() if piece != 'EMPTY'])
    
    def get_colors_around_city(self, state: GameStateDivercite, city_pos: tuple) -> list:
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

    def get_cities_affected_by_ressource(self, state: GameStateDivercite, ressource_pos: tuple) -> dict:
        adjacent_positions = state.get_neighbours(ressource_pos[0], ressource_pos[1])
        adjacent_cities = {}
        
        for direction, (piece, pos) in adjacent_positions.items():
            if piece != 'EMPTY' and hasattr(piece, 'get_type'):
                piece_type = piece.get_type()
                if piece_type[1] == 'C':
                    adjacent_cities.update({pos: piece_type})
        
        return adjacent_cities

    def evaluate_resource_scarcity(self, state: GameStateDivercite) -> float:
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

    def evaluate_ressource_placement(self, state: GameStateDivercite) -> float:
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
    
    def evaluate_city_placement(self, state: GameStateDivercite) -> float:
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
        
    def calculate_blocking_score(self, state: GameStateDivercite) -> float:
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
                score += 500
            elif len(unique_colors) == 2 and len(adjacent_colors) == 3 and adjacent_colors.count(blocking_color) == 1:
                score += 50
        return score
         
    def calculate_divercite_score(self, state: GameStateDivercite) -> float:
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
    
    def _evaluation(self, state: GameStateDivercite,**kwargs) -> float:
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
        