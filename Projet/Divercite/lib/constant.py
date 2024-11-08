from enum import Enum
from board_divercite import BoardDivercite
import numpy as np


BOARD_MASK = BoardDivercite.BOARD_MASK

MAX_MOVES = 20
MAX_STEP = 40

city_position = set([(1, 4),
                 (2, 3),
                 (2, 5),
                 (3, 2),
                 (3, 4),
                 (3, 6),
                 (4, 1),
                 (4, 3),
                 (4, 5),
                 (4, 7),
                 (5, 2),
                 (5, 4),
                 (5, 6),
                 (6, 3),
                 (6, 5),
                 (7, 4)])

corner_city_position = set([
    (1, 4), (4, 1), (4, 7), (7, 4)
])

no_corner_city_position = set(city_position).difference(corner_city_position)

center_city_position = set([(4, 3), (4, 5), (3, 4), (5, 4)])

no_corner_no_center_city_position = no_corner_city_position.difference(center_city_position)


ressources_position = set([(0, 4),
                       (1, 3),
                       (1, 5),
                       (2, 2),
                       (2, 4),
                       (2, 6),
                       (3, 1),
                       (3, 3),
                       (3, 5),
                       (3, 7),
                       (4, 0),
                       (4, 2),
                       (4, 4),
                       (4, 6),
                       (4, 8),
                       (5, 1),
                       (5, 3),
                       (5, 5),
                       (5, 7),
                       (6, 2),
                       (6, 4),
                       (6, 6),
                       (7, 3),
                       (7, 5),
                       (8, 4)])

outside_ressources_position = set([
    (4, 0), (3, 1), (2, 2), (1, 3), (0, 4), (1, 5), (2, 6),(
        3, 7), (4, 8), (5, 7), (6, 5), (7, 4)
])

corner_ressource_position =set([
    (4,0),(0,4),(8,4),(4,8)
])

center_ressources_position = ressources_position.difference(outside_ressources_position)



horizontal_vertical_compute = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
diagonal_compute = [(2,0),(0,2),(-2,0),(0,-2)]
other_type_around_compute = [(1, 0), (-1, 0), (0, 1), (0, -1)]

CITY_KEY = 'C'
RESSOURCE_KEY = 'R'
COLORS = set(['R', 'G', 'B', 'Y'])


class RessourcesNames(Enum):
    RR = 'RR'
    GR = 'GR'
    YR = 'YR'
    BR = 'BR'


class CityNames(Enum):
    RC = 'RC'
    GC = 'GC'
    YC = 'YC'
    BC = 'BC'


def is_city(piece_type: str): ...


def is_ressource(piece_type: str): ...

def is_in_board(pos:tuple[int,int]):
    x,y = pos
    return x >= 0 and y >= 0 and x<=9 and y<=9