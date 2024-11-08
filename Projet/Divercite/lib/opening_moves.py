from ._strategy import Strategy
from seahorse.game.light_action import LightAction,Action
from random import choice,shuffle
from .constant import *
from seahorse.game.game_layout.board import Piece

POSITION_KEY = 'position'
PIECE_KEY = 'piece'

############################## Simple Strategy ##########################################
class SimpleMoveStrategy(Strategy):
    def __init__(self, heuristic):
        super().__init__(heuristic)

    def search(self):
        return self.main_heuristic(self.current_state)


############################## Opening Moves Strategy ##################################
class OpeningMoveStrategy(Strategy):
    # NOTE if theres multiple opening strategy, move the code to a heuristic
    def __init__(self,force_same_color:bool = True):
        self.force_same_color = force_same_color

    def search(self) -> Action:
    
        if self.current_state.step == 1: # Second move of the game
            last_move = self.last_move
            pieces:Piece = self.current_state.rep.env[last_move]
            c,t,_ = pieces.piece_type
            
        if self.my_step == 0: # First time to play
            if self.is_first_to_play:
                return LightAction({POSITION_KEY: choice(center_city_position), PIECE_KEY: choice(CityNames._member_names_)})
                
            piece = c+CITY_KEY if self.force_same_color else choice(COLORS)+CITY_KEY
            self.fist_move_color,_ = piece

            if t == CITY_KEY:
                return LightAction({POSITION_KEY: self._check_city_in_center(last_move,horizontal_vertical_compute), PIECE_KEY: piece })
            
            return LightAction({POSITION_KEY: self._check_city_in_center(last_move,around_type_compute), PIECE_KEY: piece})

        ## second action
        if c != self.fist_move_color and self.force_same_color: # NOTE and depends on [force_same_flag] flag
            new_color = c
        else:
            # the colors least used by the oppoennent
            new_color = choice(set(COLORS).difference([self.fist_move_color]))
            
        if t == RESSOURCE_KEY:
            piece = new_color+CITY_KEY
            return LightAction({POSITION_KEY: self._check_city_in_center(last_move,around_type_compute), PIECE_KEY: piece})
        




    def _check_city_in_center(self,pos,index_compute,preferred_pos = no_corner_city_position,fallback_pos = None):
             
        if fallback_pos == None:
            fallback_pos = preferred_pos
        new_pos = None
        n_index = len(index_compute)
        shuffle(index_compute)

        for index in range(n_index):
            i,j = index_compute[index]
            x,y = pos  
            new_pos = x+i,y+j
            if new_pos in preferred_pos:
                return new_pos
        
        return choice(fallback_pos)

    def _minimize_distance(self,):
        available_nice_city_position = list(set(no_corner_city_position).difference(self.moves))
        available_nice_city_position = np.array(available_nice_city_position)


        ...