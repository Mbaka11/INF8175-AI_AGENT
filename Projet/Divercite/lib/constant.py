from enum import Enum
from board_divercite import BoardDivercite


BOARD_MASK = BoardDivercite.BOARD_MASK
MAX_MOVES = 20
MAX_STEP = 40

city_position = [(1, 4),
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
                 (7, 4)]

corner_city_position = [
    (1, 4), (4, 1), (4, 7), (7, 4)
]

no_corner_city_position = list(
    set(city_position).difference(corner_city_position))

center_city_position = [(4, 4), (4, 6), (5, 5), (3, 5)
                        ]

horizontal_vertical_compute = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
around_type_compute = [(1, 0), (-1, 0), (0, 1), (0, -1)]

CITY_KEY = 'C'
RESSOURCE_KEY = 'R'
COLORS = ['R', 'G', 'B', 'Y']


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
