"""Piece-square tables used by the evaluation function.

Each table is indexed by a square (0..63) in python-chess's
internal order, assuming we look from White's perspective.
Positive values indicate that the piece likes being on that
square, negative values that it dislikes it.

Black uses the same tables but with `chess.square_mirror`, so
we can evaluate both sides symmetrically.
"""

# Pawn piece-square table.
#
# - Pawns get bonuses for advancing to the 3rd/4th ranks and
#   especially for occupying central files.
# - Small penalties encourage avoiding backward or overextended
#   pawns in some structures.
PAWN_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]

# Knight piece-square table.
#
# - Strongly penalizes knights on the edge/corners (they control
#   fewer squares there).
# - Rewards central, active knight positions in the middle of the
#   board where they influence many squares.
KNIGHTS_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

# Bishop piece-square table.
#
# - Encourages bishops to operate on long diagonals and in central
#   regions where their range is maximized.
# - Slight penalties for being stuck on the back rank or blocked
#   by own pawns.
BISHOPS_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

# Rook piece-square table.
#
# - Rooks prefer to be on open or semi-open files and further up
#   the board where they can attack along ranks and files.
ROOKS_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0
]

# Queen piece-square table.
#
# - Queens get bonuses for centralization and activity.
# - Slight penalties near the edges discourage putting the queen
#   on the rim too early where it can be chased around.
QUEENS_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
    0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

# King piece-square table (middle-game oriented).
#
# - Strongly penalizes kings in the center of the board where they
#   are exposed to attacks.
# - Rewards castled positions and "tucked away" kings behind pawn
#   shields on the back rank.
KINGS_TABLE = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]