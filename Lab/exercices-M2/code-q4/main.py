import argparse
import time
from bg_board import BGBoard
from game_state_connect4 import GameStateConnect4
from master import Master
from game_state_tictac import GameStateTictac
from my_player_bg import MyPlayerBG

def play(game, player1, player2, log_level, port, address) :

    list_players = [player1, player2]
    init_scores = {player1.get_id(): 0, player2.get_id(): 0}
    dim = [6, 7] if game == "connect4" else [3, 3]
    init_rep = BGBoard(env={}, dim=dim)
    initial_game_state = GameStateConnect4(
        scores=init_scores, next_player=player1, players=list_players, rep=init_rep) \
    if game == "connect4" else \
    GameStateTictac(
        scores=init_scores, next_player=player1, players=list_players, rep=init_rep
    )

    master = Master(
        name=game, initial_game_state=initial_game_state, players_iterator=list_players, log_level=log_level, port=port, hostname=address
    )
    master.record_game()

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('--scenario', type=str, default="test")

    return parser.parse_args()

if __name__=="__main__":
    args = parse_arguments()
    start_time = time.time()

    if args.scenario == "test":
        print("Random (X) vs Random (O) on tic-tac-toe")
        print("Only used to check that the code is working in your system")

        strategy1 = "random"
        strategy2 = "random"
        game = "tictactoe"

    elif args.scenario == "S1":
        print("Random (X) vs Minimax (O) on tic-tac-toe")
        print("You should observe that Minimax never loses to game (a draw is possible)")

        strategy1 = "random"
        strategy2 = "minimax"
        game = "tictactoe"

    elif args.scenario == "S2":
        print("Random (X) vs Minimax (O) on Connect Four")
        print("You should observe that Minimax is very slow")
        print("It is because the search space is too large")
        print("You can stop the execution")

        strategy1 = "random"
        strategy2 = "minimax"
        game = "connect4"

    elif args.scenario == "S3":
        print("Random (X) vs AlphaBeta (O) on tic-tac-toe")
        print("You should observe that AlphaBeta never loses to game (a draw is possible)")

        strategy1 = "random"
        strategy2 = "alphabeta"
        game = "tictactoe"

    elif args.scenario == "S4":
        print("Random (X) vs AlphaBeta (O) on Connect Four")
        print("You should observe that AlphaBeta is very slow")
        print("It is because the search space is too large, even with pruning")
        print("You can stop the execution")

        strategy1 = "random"
        strategy2 = "alphabeta"
        game = "connect4"


    elif args.scenario == "S5":
        print("minimax (X) vs AlphaBeta (O) on tic-tac-toe")

        strategy1 = "minimax"
        strategy2 = "alphabeta"
        game = "tictactoe"

    elif args.scenario == "S6":
        print("Random (X) vs AlphaBeta with a cutoff (O) on Connect Four ")
        print("Cutoff is done at depth 6")

        strategy1 = "random"
        strategy2 = "h_alphabeta"
        game = "connect4"

    elif args.scenario == "S7":
        print("Your agent (X) vs AlphaBeta with a cutoff (O) on Connect Four ")
        print("Cutoff is done at depth 6")

        strategy1 = "your_player"
        strategy2 = "h_alphabeta"
        game = "connect4"

    else:
        print("Invalid scenario")
        exit()

    player1 = MyPlayerBG("X", name=f"{game}_{strategy1}_1", strategy=strategy1)
    player2 = MyPlayerBG("O", name=f"{game}_{strategy2}_2", strategy=strategy2)

    play(game=game, player1=player1, player2=player2, log_level="INFO", port=16001, address="127.0.0.1")

    end_time = time.time() - time.time()

    print("Elapsed: %.2f seconds" % (time.time() - start_time))