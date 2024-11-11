from game_state_divercite import GameStateDivercite
from .definition import Strategy,Heuristic,SimpleMoveHeuristic
from seahorse.game.light_action import LightAction,Action
from random import choice,shuffle
from .constant import *
from seahorse.game.game_layout.board import Piece

POSITION_KEY = 'position'
PIECE_KEY = 'piece'

class OpeningHeuristic(SimpleMoveHeuristic):

    def __init__(self,force_same_color:bool = True):
        self.force_same_color = force_same_color
        self.last_color_played = None

        self.center_city_position = center_city_position.copy()
    
    def evaluate(self, current_state:GameStateDivercite,first_to_play:bool,last_move:tuple[int,int]):
        # NOTE forcing the same color or a different might not necessary be a better move
        if first_to_play and current_state.step ==0 :
            city = choice(CityNames._member_names_)
            self.last_color_played,_ = city
            pos=choice(list(center_city_position))
            self.center_city_position.difference_update([pos])
            return LightAction({POSITION_KEY: pos, PIECE_KEY: city})
     
        pieces:Piece = current_state.rep.env[last_move]
        c,t,_ = pieces.piece_type


        if  current_state.step >=2:
            if c == self.last_color_played:
                c= choice(list(COLORS.difference([c])))
            piece =  c+CITY_KEY 

        else:
            piece = c+CITY_KEY if self.force_same_color else choice(CityNames._member_names_)
            self.last_color_played,_= piece


        self.center_city_position.difference_update([last_move])
        if t == CITY_KEY:
                
                if last_move in center_city_position:
                    
                    index_compute = horizontal_vertical_compute if self.force_same_color else diagonal_compute # BUG Hyperparameter to test, based on statistic wether we play the same color or not 
                    return LightAction({POSITION_KEY: self.check_certain_position(last_move,index_compute,self.center_city_position), PIECE_KEY: piece })

                if last_move in corner_city_position:
                    # BUG Might not be ideal to play close to the player since it can rob our divercity or point
                    c_2 = self.last_color_played if self.last_color_played != None else c
                    c = choice(list(COLORS.difference([c,c_2])))
                    self.last_color_played = c

                    return LightAction({POSITION_KEY: self.check_certain_position(last_move,diagonal_compute,self.center_city_position), PIECE_KEY:c+CITY_KEY  })
                
                self.last_color_played = c
                return LightAction({POSITION_KEY: self.check_certain_position(last_move,horizontal_vertical_compute,self.center_city_position), PIECE_KEY: c+CITY_KEY  })
                
 
        if last_move in center_ressources_position:

            neighbors = current_state.get_neighbours(last_move[0],last_move[1])
            neighbors = [ v[1] for _,v in neighbors.items()]
            neighbors = choice(list(self.center_city_position.intersection(neighbors)))
            self.last_color_played = c
            return LightAction({POSITION_KEY: neighbors, PIECE_KEY: c+CITY_KEY})

        pos = self._minimize_maximize_distance(last_move,self.center_city_position)
        
        return LightAction({POSITION_KEY: pos, PIECE_KEY: piece})


class RandomMoveHeuristic(SimpleMoveHeuristic):
    def evaluate(self, current_state):
        return choice(list(current_state.get_possible_light_actions())) 

############################## Simple Strategy ##########################################
class SimpleMoveStrategy(Strategy):
    def __init__(self, heuristic):
        super().__init__(heuristic)

    def search(self):
        return self.main_heuristic(self.current_state)


############################## Opening Moves Strategy ##################################
class OpeningMoveStrategy(Strategy):
    # NOTE if theres multiple opening strategy, move the code to a heuristic
    def __init__(self,opening_heuristic:SimpleMoveHeuristic,):
        super().__init__(opening_heuristic)

    def search(self) -> Action:
        return self.main_heuristic(self.current_state,first_to_play = self.is_first_to_play,last_move=self.last_move)

