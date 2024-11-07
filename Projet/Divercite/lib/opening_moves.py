from ._strategy import Strategy
from seahorse.game.light_action import LightAction,Action
from random import choice,shuffle
from .constant import *
from seahorse.game.game_layout.board import Piece

POSITION_KEY = 'position'
PIECE_KEY = 'piece'


class SimpleMoveStrategy(Strategy):
    def __init__(self, heuristic):
        super().__init__(heuristic)

    def search(self):
        return self.main_heuristic(self.current_state)


class OpeningMoveStrategy(Strategy):
    def __init__(self,force_same_color:bool = True):
        self.force_same_color = force_same_color

    def search(self) -> Action:
    
        if self.is_first_move:
            return LightAction({POSITION_KEY: choice(center_city_position), PIECE_KEY: choice(CityNames._member_names_)})
     
        last_move = self.last_move
        pieces:Piece = self.current_state.rep.env[last_move]
        c,t,_ = pieces.piece_type
        piece = c+CITY_KEY if self.force_same_color else choice(COLORS)+CITY_KEY

        if t == CITY_KEY:
            return LightAction({POSITION_KEY: self._check_city_in_center(last_move,horizontal_vertical_compute), PIECE_KEY: piece })
        
        return LightAction({POSITION_KEY: self._check_city_in_center(last_move,around_type_compute), PIECE_KEY: piece})

    def _check_city_in_center(self,pos,index_compute,):
        
        new_pos = None
        n_index = len(index_compute)
        shuffle(index_compute)

        for index in range(n_index):
            i,j = index_compute[index]
            x,y = pos  
            new_pos = x+i,y+j
            if new_pos in center_city_position:
                return new_pos
        
        return choice(center_city_position)

