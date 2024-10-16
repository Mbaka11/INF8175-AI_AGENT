import copy
import json
from math import sqrt
from typing import Generator, Optional

from bg_board import BGBoard
from bg_player import BGPlayer

from seahorse.game.heavy_action import HeavyAction
from seahorse.game.light_action import LightAction
from seahorse.game.game_layout.board import Piece
from seahorse.game.game_state import GameState
from seahorse.game.representation import Representation
from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable


class GameStateTictac(GameState):
    """
    A class representing the game state for Tic-Tac-Toe.

    Attributes:
        score (List[float]): The scores of the state for each player.
        next_player (Player): The next player to play.
        players (List[Player]): The list of players.
        rep (BoardTictac): The representation of the game.
    """

    def __init__(self, scores: dict, next_player: Player, players: list[Player], rep: BGBoard, *_, **__) -> None:
        """
        Initializes a new instance of the GameStateTictac class.

        Args:
            scores (Dict): The scores of the state for each player.
            next_player (Player): The next player to play.
            players (List[Player]): The list of players.
            rep (BoardTictac): The representation of the game.
        """
        super().__init__(scores, next_player, players, rep)
        self.num_pieces = self.get_rep().get_dimensions()[0] * self.get_rep().get_dimensions()[1]

    def get_num_pieces(self) -> int:
        """
        Returns the number of pieces implied in the game.

        Returns:
            num_pieces (int): The number of pieces implied in the game.
        """
        return self.num_pieces

    def is_done(self) -> bool:
        """
        Checks if the game is finished.

        Returns:
            bool: True if the game is finished, False otherwise.
        """
        if len(self.rep.get_env().keys()) == self.num_pieces or self.has_won():
            return True
        return False

    def generate_possible_heavy_actions(self) -> Generator[HeavyAction, None, None]:
        """
        Generates possible actions.

        Returns:
            Generator[HeavyAction]: The possible actions.
        """
        current_rep = self.get_rep()
        b = current_rep.get_env()
        d = current_rep.get_dimensions()
        next_player = self.get_next_player()
        for i in range(d[0]):
            for j in range(d[1]):
                if not current_rep.get_env().get((i, j)):
                    copy_b = copy.copy(b)
                    copy_b[(i, j)] = Piece(piece_type=next_player.get_piece_type(), owner=next_player)
                    new_board = BGBoard(copy_b, d)
                    yield HeavyAction(
                        self,
                        GameStateTictac(
                            self.compute_scores(new_board),
                            self.compute_next_player(),
                            self.players,
                            new_board,
                        ),
                    )

    def generate_possible_light_actions(self) -> Generator[LightAction, None, None]:
        """
        Generates possible actions.

        Returns:
            Generator[LightAction]: The possible actions.
        """
        current_rep = self.get_rep()
        b = current_rep.get_env()
        d = current_rep.get_dimensions()
        next_player = self.get_next_player()
        for i in range(d[0]):
            for j in range(d[1]):
                if not current_rep.get_env().get((i, j)):
                    yield LightAction(
                        data={"position": (i,j), "piece_type": next_player.get_piece_type()},
                    )

    def apply_action(self, action: LightAction) -> GameState:
        """
        Applies an action to the game state.

        Args:
            action (LightAction): The action to apply.

        Returns:
            GameState: The new game state.
        """
        (i,j) = action.data["position"]
        piece_type = action.data["piece_type"]
        current_rep = self.get_rep()
        b = current_rep.get_env()
        d = current_rep.get_dimensions()
        next_player = self.get_next_player()
        copy_b = copy.copy(b)
        copy_b[(i, j)] = Piece(piece_type=piece_type, owner=next_player)
        new_board = BGBoard(copy_b, d)
        return GameStateTictac(
            self.compute_scores(new_board),
            self.compute_next_player(),
            self.players,
            new_board,
        )
        
    def compute_scores(self, representation: Representation) -> dict[int, float]:
        scores = {player.get_id(): 0.0 for player in self.players}
        bound = 2.0
        dim = representation.get_dimensions()[0]
        env = representation.get_env()

        for player in self.players:
            player_id = player.get_id()
            rows, cols, diag1, diag2 = [0]*dim, [0]*dim, 0, 0

            for i in range(dim):
                for j in range(dim):
                    if env.get((i, j), None) and env[(i, j)].get_owner_id() == player_id:
                        rows[i] += 1
                        cols[j] += 1
                        if i == j:
                            diag1 += 1
                        if i + j == dim - 1:
                            diag2 += 1

            if any(count > bound for count in rows + cols) or diag1 > bound or diag2 > bound:
                scores[player_id] = 1.0
                scores[next(iter(set(self.players) - {player})).get_id()] = -1.0

        return scores

    def has_won(self) -> bool:
        """
        Checks if a player has won the game.

        Returns:
            bool: True if a player has won, False otherwise.
        """
        return any(score > 0.0 for score in self.scores.values())

    def __str__(self) -> str:
        if not self.is_done():
            return super().__str__()
        return "The game is finished!"

    def to_json(self) -> dict:
        return { i:j for i,j in self.__dict__.items() if not i.startswith("_")}

    @classmethod
    def from_json(cls,data:str,*,next_player:Optional[BGPlayer]=None) -> Serializable:
        d = json.loads(data)
        return cls(**{**d,"scores":{int(k):v for k,v in d["scores"].items()},"players":[BGPlayer.from_json(json.dumps(x)) if not isinstance(x,str) else next_player for x in d["players"]],"next_player":next_player,"rep":BoardTictac.from_json(json.dumps(d["rep"]))})
