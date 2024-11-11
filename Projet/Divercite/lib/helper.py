
def is_city(piece_type: str): ...


def is_ressource(piece_type: str): ...

def is_in_board(pos:tuple[int,int]):
    x,y = pos
    return x >= 0 and y >= 0 and x<=9 and y<=9