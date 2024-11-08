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
        
        match self.current_state.step:
            case 0:
                ...
            case 1:
                ...
            case 2:
                ...
            case 3:
                ...
