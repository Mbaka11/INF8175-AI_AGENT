from game_state_divercite import GameStateDivercite


class Algorithm:
    MAX_STEP:int = None
    current_step:int = None
    my_player_id:int = None
    opponent_id:int = None
    is_started: bool =None
    
    @staticmethod
    def set_current_state(current_state):
        ...
    
    def compute_best_moves(self):
        ...