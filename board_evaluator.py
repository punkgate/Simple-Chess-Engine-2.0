import chess
from board_pieces_tables import *


# Large score used to represent a decisive result (mate).
# The sign still follows the "from White's perspective" rule:
#   +MATE_SCORE  -> forced win for White
#   -MATE_SCORE  -> forced win for Black
MATE_SCORE = 100000


def evaluate(board: chess.Board) -> int:
    """Evaluate a position from White's perspective.

    Positive scores are good for White, negative scores are good
    for Black. This function combines:

    - Game-ending results (checkmates, draws)
    - Material balance (piece counts and standard piece values)
    - Piece-square tables (activity, centralization, king safety)
    """

    # 1. Handle terminal positions (checkmate, stalemate, etc.) first.
    #    This makes the engine strongly prefer actually delivering mate
    #    over just being a lot of material up.
    if board.is_game_over():
        outcome = board.outcome(claim_draw=True)
        # outcome.winner is None for draws and stalemates.
        if outcome is None or outcome.winner is None:
            return 0
        # If White wins, return a very large positive score; if Black
        # wins, return a very large negative score.
        return MATE_SCORE if outcome.winner == chess.WHITE else -MATE_SCORE

    # 2. Material: count each type of piece for both sides.
    wp = len(board.pieces(chess.PAWN, chess.WHITE))
    bp = len(board.pieces(chess.PAWN, chess.BLACK))
    wn = len(board.pieces(chess.KNIGHT, chess.WHITE))
    bn = len(board.pieces(chess.KNIGHT, chess.BLACK))
    wb = len(board.pieces(chess.BISHOP, chess.WHITE))
    bb = len(board.pieces(chess.BISHOP, chess.BLACK))
    wr = len(board.pieces(chess.ROOK, chess.WHITE))
    br = len(board.pieces(chess.ROOK, chess.BLACK))
    wq = len(board.pieces(chess.QUEEN, chess.WHITE))
    bq = len(board.pieces(chess.QUEEN, chess.BLACK))

    # Standard piece values (in centipawns):
    #   Pawn=100, Knight=300, Bishop=300, Rook=500, Queen=900
    # The result is "White pieces minus Black pieces".
    material = 100 * (wp - bp) + 300 * (wn - bn) + 300 * (wb - bb) + 500 * (wr - br) + 900 * (wq - bq)

    # 3. Positional evaluation using piece-square tables.
    #    For White we add the table value directly.
    #    For Black we mirror the square (to reuse the same table as
    #    if they were White) and subtract the value, so the overall
    #    score is still from White's perspective.

    # Pawns: encourage advancing to good ranks and controlling center.
    pawn_sum = sum(PAWN_TABLE[i] for i in board.pieces(chess.PAWN, chess.WHITE))
    pawn_sum += sum(-PAWN_TABLE[chess.square_mirror(i)] for i in board.pieces(chess.PAWN, chess.BLACK))

    # Extra bonus for pawns that are close to promotion.
    # This makes advanced pawns (especially on the 6th/7th ranks)
    # more valuable and encourages the engine to push them.
    pawn_promotion_bonus = 0
    for sq in board.pieces(chess.PAWN, chess.WHITE):
        rank = chess.square_rank(sq)  # 0 (1st rank) .. 7 (8th rank)
        pawn_promotion_bonus += rank * 10
    for sq in board.pieces(chess.PAWN, chess.BLACK):
        rank = chess.square_rank(sq)
        # From Black's point of view, rank 0 is promotion, 7 is home rank.
        pawn_promotion_bonus -= (7 - rank) * 10

    # Knights: reward central and active knight squares, penalize edges.
    knight_sum = sum(KNIGHTS_TABLE[i] for i in board.pieces(chess.KNIGHT, chess.WHITE))
    knight_sum += sum(-KNIGHTS_TABLE[chess.square_mirror(i)] for i in board.pieces(chess.KNIGHT, chess.BLACK))

    # Bishops: reward long diagonals and central bishops.
    bishop_sum = sum(BISHOPS_TABLE[i] for i in board.pieces(chess.BISHOP, chess.WHITE))
    bishop_sum += sum(-BISHOPS_TABLE[chess.square_mirror(i)] for i in board.pieces(chess.BISHOP, chess.BLACK))

    # Rooks: prefer open/semi-open files and certain ranks.
    rook_sum = sum(ROOKS_TABLE[i] for i in board.pieces(chess.ROOK, chess.WHITE))
    rook_sum += sum(-ROOKS_TABLE[chess.square_mirror(i)] for i in board.pieces(chess.ROOK, chess.BLACK))

    # Queens: reward central, active queen positions (but not too exposed).
    queens_sum = sum(QUEENS_TABLE[i] for i in board.pieces(chess.QUEEN, chess.WHITE))
    queens_sum += sum(-QUEENS_TABLE[chess.square_mirror(i)] for i in board.pieces(chess.QUEEN, chess.BLACK))

    # Kings: this table is tuned for "middle game" king safety, where
    # central kings are penalized and castled, tucked-away kings are
    # rewarded.
    kings_sum = sum(KINGS_TABLE[i] for i in board.pieces(chess.KING, chess.WHITE))
    kings_sum += sum(-KINGS_TABLE[chess.square_mirror(i)] for i in board.pieces(chess.KING, chess.BLACK))

    # 4. Total evaluation: material + piece activity + king safety.
    boardvalue = material + pawn_sum + pawn_promotion_bonus + knight_sum + bishop_sum + rook_sum + queens_sum + kings_sum

    return boardvalue