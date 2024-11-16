from typing import Any
from game_state_divercite import GameStateDivercite
from .definition import AlgorithmHeuristic, Heuristic, ARGS_KEYS
from .constant import *
from .helper import *
import numpy as np
from random import random


class PointDifferenceHeuristic(AlgorithmHeuristic):

    def __init__(self):
        super().__init__(-30, 30, L=6)

    def _evaluation(self, current_state, **kwargs):
        my_state_score = current_state.get_scores()[kwargs['my_id']]
        opponent_state_score = current_state.get_scores()[
            kwargs['opponent_id']]

        my_current_score = kwargs['my_score']
        opponent_current_score = kwargs['opponent_score']

        return self._maximize_score_diff(my_current_score, opponent_current_score, my_state_score, opponent_state_score)


class ControlIndexHeuristic(AlgorithmHeuristic):

    def __init__(self):
        super().__init__(0, 1,)

    def _evaluation(self, current_state, **kwargs):
        my_piece_type = kwargs['my_piece_type']
        original_env: dict = kwargs['current_env']
        opp_piece_type = kwargs['opponent_piece_type']
        state_env = current_state.rep.env

        (my_state_moves, my_ic_state), (opp_state_moves, opp_ic_state) = self._filter_moves_control_index(
            current_state.rep.env, my_piece_type)
        (my_current_moves, my_current_ic), (opp_current_moves, opp_current_ic) = self._filter_moves_control_index(
            original_env, my_piece_type)

        ic_control_index = self._maximize_score_diff(
            my_current_ic, opp_current_ic, my_ic_state, opp_ic_state)

        my_current_dist = self._compute_distances(
            my_piece_type, my_current_moves, original_env)
        opp_current_dist = self._compute_distances(
            opp_piece_type, opp_current_moves, original_env)

        my_state_dist = self._compute_distances(
            my_piece_type, my_state_moves, state_env)
        opp_state_dist = self._compute_distances(
            opp_piece_type, opp_state_moves, state_env)

        dist_index = self._maximize_score_diff(
            my_current_dist, opp_current_dist, my_state_dist, opp_state_dist)

        # print('IC index:',ic_control_index)
        # print('Distance index:',dist_index)
        # print('Evaluation:',ic_control_index+dist_index)
        # print('--'*10)

        return ic_control_index + dist_index  #NOTE we can add weight it depends on which is more important

    def _compute_distances(self, pieces_type: str, added_moves: dict[tuple, str], state_env: dict[tuple, str]):
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
                    score += (5 if in_horizontal else 10)

                elif c == p_color and pieces_type != p_owner:  # same color but diff ownership
                    score += (15 if in_horizontal else 10)

                elif c != p_color and pieces_type == p_owner:  # diff color but same ownership
                    score += (15 if in_horizontal else 10)
                else:                # different ownership and diff_color
                    score += (20 if in_horizontal else 15)

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

        # if return_ic:
        #     # return (my_moves,my_ic),(opp_moves,my_ic)
        #     return my_ic, opp_ic

        return (my_moves, my_ic), (opp_moves, opp_ic)


class PiecesVarianceHeuristic(AlgorithmHeuristic):

    def __init__(self, city_weight=.7, ress_weight=.3):
        super().__init__(-300, -4, L=4.3)
        self.city_weight = city_weight
        self.ress_weight = ress_weight

    def _evaluation(self, current_state, **kwargs):
        opponent_pieces = current_state.players_pieces_left[kwargs['opponent_id']]
        my_pieces = current_state.players_pieces_left[kwargs['my_id']]

        #####
        my_state_var = self._pieces_var(my_pieces)
        opp_state_var = self._pieces_var(opponent_pieces)

        return  opp_state_var-my_state_var
        
        

    def _pieces_var(self, pieces: dict[str, int]):
        city_val = np.array([pieces[cn] for cn in CityNames._member_names_])
        ress_val = np.array([pieces[rn]
                            for rn in RessourcesNames._member_names_])
        score_city = np.var(city_val)*100
        score_ress = np.var(ress_val)*100

        score_city = 25 if score_city == 0 else score_city
        score_ress = 40 if score_ress == 0 else score_ress
        return (score_city*self.city_weight + score_ress*self.ress_weight)/self._h_tot_weight

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
