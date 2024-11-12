from random import shuffle,choice
from .constant import no_corner_city_position,AROUND_CITY,center_city_position,CENTER_CITY,CORNER_CITY,city_index_control
import numpy as np

def is_city(piece_type: str): ...

def is_ressource(piece_type: str): ...

def is_in_board(pos:tuple[int,int]):
    x,y = pos
    return x >= 0 and y >= 0 and x<=9 and y<=9
################################################################
def check_certain_position(pos, index_compute, preferred_pos=no_corner_city_position, fallback_pos=None):

        if fallback_pos == None:
            fallback_pos = preferred_pos

        new_pos = None
        n_index = len(index_compute)
        shuffle(index_compute)

        for index in range(n_index):
            i, j = index_compute[index]
            x, y = pos
            new_pos = x+i, y+j
            if new_pos in preferred_pos and is_in_board(new_pos):
                return new_pos

        return choice(list(fallback_pos))

def minimize_maximize_distance(x, preferred_position: set, is_min=True):
        # NOTE might put in a helper
        available_position = list(preferred_position)
        distances = (np.array(available_position) - np.array([x]))**2
        dist_position: np.ndarray = np.apply_along_axis(
            np.sum, axis=1, arr=distances)
        
        dist_position = dist_position.argmin(
        ) if is_min else dist_position.argmax()
        print(dist_position)
        return available_position[int(dist_position)]
################################################################

def control_index(city_pos:tuple):
    if city_pos in no_corner_city_position:
        return city_index_control[AROUND_CITY]
    if city_pos in center_city_position:
        return city_index_control[CENTER_CITY]
    
    return city_index_control[CORNER_CITY]