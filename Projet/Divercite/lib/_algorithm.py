from .heuristic import Heuristic
from game_state_divercite import GameStateDivercite


class Algorithm:
    
    is_first_move: bool = None
    current_state: GameStateDivercite = None
    my_id: int = None
    opponent_id: int = None
    remaining_time: float = None
    my_step:int = 0 
    
    @staticmethod
    def set_current_state(current_state:GameStateDivercite,remaining_time: float):
        Algorithm.current_state = current_state
        Algorithm.remaining_time = remaining_time
        Algorithm.my_step+=1
        if Algorithm.my_step == 1:
            Algorithm.init_game_state()
        
    @staticmethod
    def init_game_state():
        Algorithm.opponent_id = Algorithm.current_state.compute_next_player().id
        temp = [ player.id for player in Algorithm.current_state.players]
        Algorithm.my_id = temp.remove(Algorithm.opponent_id)[0]    
        Algorithm.is_first_move = Algorithm.my_step == Algorithm.current_state.step
    
    def __init__(self,heuristic:Heuristic):
        self.heuristic: Heuristic = heuristic
        pass

    def compute_best_moves(self):
        pass
    