import chess

from board_evaluator import evaluate


class console_colors:
    """ANSI console color escape codes used by the CLI interface.

    This is only used by the text-based mode at the bottom of this
    file and has no impact on the GUI. It simply makes the terminal
    output a bit nicer when playing in the console.
    """

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def _determine_best_move(board: chess.Board, is_white: bool, depth: int = 4) -> chess.Move | None:
    """Return the best move for the side to move using minimax.

    The engine iterates over every legal move in the current
    position, evaluates the resulting positions using a depth-limited
    minimax search with alpha–beta pruning, and returns the move
    that leads to the best score according to `evaluate`.

    Args:
        board: Current board position to analyze.
        is_white: True if the player to move is White, False for Black.
        depth: Search depth in plies (half-moves).
    """

    # Initial best score depends on which side is searching: White
    # tries to maximize the evaluation, Black tries to minimize it.
    best_move_value = -100000 if is_white else 100000
    best_final: chess.Move | None = None
    # Try every legal move from this position.
    for move in board.legal_moves:
        board.push(move)
        value = _minimax_helper(depth - 1, board, -10000, 10000, not is_white)
        board.pop()
        if (is_white and value > best_move_value) or (not is_white and value < best_move_value):
            best_move_value = value
            best_final = move
    return best_final


def _minimax_helper(depth: int, board: chess.Board, alpha: int, beta: int, is_maximizing: bool) -> int:
    """Recursive minimax search with alpha–beta pruning.

    `evaluate` always scores positions from White's perspective, so
    when `is_maximizing` is True we behave as "White" (maximize the
    score), and when it is False we behave as "Black" (minimize it).

    Alpha and beta track the best already-known scores for the
    maximizing and minimizing players respectively; if a branch can
    no longer influence the final result we prune it.
    """

    # If we reached the depth limit or the game is over (checkmate,
    # stalemate, etc.), we return a static evaluation of the position.
    if depth <= 0 or board.is_game_over():
        return evaluate(board)

    if is_maximizing:
        # Maximizing player (White in our scoring scheme).
        best_move_value = -100000
        for move in board.legal_moves:
            board.push(move)
            value = _minimax_helper(depth - 1, board, alpha, beta, False)
            board.pop()
            best_move_value = max(best_move_value, value)
            alpha = max(alpha, best_move_value)
            if beta <= alpha:
                # Beta cut-off: the minimizing side already has a
                # better option, so exploring further moves here
                # cannot improve the final result.
                break
        return best_move_value
    else:
        # Minimizing player (Black in our scoring scheme).
        best_move_value = 100000
        for move in board.legal_moves:
            board.push(move)
            value = _minimax_helper(depth - 1, board, alpha, beta, True)
            board.pop()
            best_move_value = min(best_move_value, value)
            beta = min(beta, best_move_value)
            if beta <= alpha:
                # Alpha cut-off: the maximizing side already has a
                # better option, so exploring further moves here
                # cannot improve the final result.
                break
        return best_move_value

if __name__ == '__main__':
    board = chess.Board()

    print(console_colors.HEADER + f'==================================================' + console_colors.ENDC)
    print(console_colors.HEADER + f'                   Chess Engine                   ' + console_colors.ENDC)
    print(console_colors.HEADER + f'==================================================' + console_colors.ENDC)
    print()

    is_white = input(console_colors.OKBLUE + 'Will you be playing as white or black (white/black)? ' + console_colors.ENDC).lower()[0] == "w"

    print()
    print(console_colors.HEADER + f'= Board State =' + console_colors.ENDC)
    print(board)

    if is_white:
        while not board.is_game_over():
            print()
            while True:
                try:
                    move = board.parse_san(input(console_colors.OKGREEN + 'Enter your move: ' + console_colors.ENDC))
                except ValueError:
                    print(console_colors.FAIL + f'That is not a valid move!' + console_colors.ENDC)
                    continue
                break
            board.push(move)

            move = _determine_best_move(board, False)
            board.push(move)

            print()
            print(console_colors.FAIL + f'Black made the move: {move}' + console_colors.ENDC)
            print()
            print(console_colors.HEADER + f'= Board State =' + console_colors.ENDC)
            print(board)
            print()
    else:
        while not board.is_game_over():
            move = _determine_best_move(board, True)
            board.push(move)

            print()
            print(console_colors.FAIL + f'White made the move: {move}' + console_colors.ENDC)
            print()
            print(console_colors.HEADER + f'= Board State =' + console_colors.ENDC)
            print(board)

            print()
            while True:
                try:
                    move = board.parse_san(input(console_colors.OKGREEN + 'Enter your move: ' + console_colors.ENDC))
                except ValueError:
                    print(console_colors.FAIL + f'That is not a valid move!' + console_colors.ENDC)
                    continue
                break
            board.push(move)

    print(console_colors.HEADER + f'The game is over!' + console_colors.ENDC)
