Simple Chess Engine
===================

A simple chess engine with a Tkinter GUI, built in Python on top of the `python-chess` library.

> Attribution: This project is built on top of, and heavily inspired by, the original GitHub project by Kyle L:
> https://github.com/Kyle-L/Simple-Chess-Engine

Project Structure
-----------------

- `engine.py` – search logic (minimax + alpha–beta pruning) and a simple console mode.
- `board_evaluator.py` – position evaluation (material, piece–square tables, pawn promotion potential).
- `board_pieces_tables.py` – piece–square tables for all pieces.
- `gui.py` – Tkinter GUI for playing against the engine.
- `requirements.txt` / `pyproject.toml` – dependencies (mainly `python-chess`).

How the Engine Thinks
---------------------

### Minimax overview

The core search uses a classic **minimax** algorithm over the game tree.

- The tree nodes are chess positions (`chess.Board`).
- Edges are legal moves from each position.
- White is the **maximizing** player: tries to maximize the evaluation.
- Black is the **minimizing** player: tries to minimize the evaluation.

Conceptually, for a given depth (in plies):

- At a White node: choose the child with the **max** score.
- At a Black node: choose the child with the **min** score.

In `engine.py` this is implemented as:

- `_determine_best_move(board, is_white, depth)`
	- Loops over all `board.legal_moves`.
	- For each move, `board.push(move)`, calls `_minimax_helper(...)`, then `board.pop()`.
	- Tracks the move with the best resulting score.
- `_minimax_helper(depth, board, alpha, beta, is_maximizing)`
	- Recursively explores the game tree until `depth == 0` or the game is over.
	- Calls `evaluate(board)` from `board_evaluator.py` at the leaves.

### Alpha–beta pruning

Alpha–beta pruning is used inside `_minimax_helper` to cut off branches that cannot influence the final decision.

- `alpha` – the best value found so far for the maximizing player (White).
- `beta` – the best value found so far for the minimizing player (Black).

Pruning rules:

- In a maximizing node:
	- After updating `best_move_value`, set `alpha = max(alpha, best_move_value)`.
	- If `beta <= alpha`, further children cannot improve the outcome → **beta cut-off**.
- In a minimizing node:
	- After updating `best_move_value`, set `beta = min(beta, best_move_value)`.
	- If `beta <= alpha`, further children cannot improve the outcome → **alpha cut-off**.

This doesn’t change the final best move compared to plain minimax, but it often skips large parts of the tree and makes the engine much faster.

Position Evaluation
-------------------

All evaluation is done in `board_evaluator.py` by the function `evaluate(board)`, which always returns a score **from White’s perspective**:

- Positive score → good for White.
- Negative score → good for Black.

### 1. Terminal positions

First, the code checks `board.is_game_over()` and uses `board.outcome(claim_draw=True)`:

- If the game is a draw or stalemate → return `0`.
- If White wins → return a large positive `MATE_SCORE`.
- If Black wins → return `-MATE_SCORE`.

This strongly prefers actually checkmating the opponent over simply being up material.

### 2. Material balance

Material is counted using basic piece values (in centipawns):

- Pawn = 100
- Knight = 300
- Bishop = 300
- Rook = 500
- Queen = 900

For each side, the number of each piece type is multiplied by its value, and the final material score is:

- `material = (White pieces) − (Black pieces)`

So a positive material score means White has more or better pieces.

### 3. Piece–square tables (positional heuristics)

Positional ideas are encoded via piece–square tables in `board_pieces_tables.py`:

- `PAWN_TABLE`
- `KNIGHTS_TABLE`
- `BISHOPS_TABLE`
- `ROOKS_TABLE`
- `QUEENS_TABLE`
- `KINGS_TABLE` (tuned for middlegame king safety)

The tables are written **from White’s point of view** (more central and active squares usually get higher values).

For White pieces:

- Directly sum the table values for the squares where those pieces live.

For Black pieces:

- Mirror the square with `chess.square_mirror(i)` and subtract the table value.

This keeps everything in a single “White’s perspective” scale. Examples of what the tables encourage:

- Pawns advancing toward the center and up the board.
- Knights in the center instead of on the edge.
- Bishops on long diagonals.
- Rooks on open/semi-open files and active ranks.
- Queens more central but not stuck on the rim.
- Kings safer on the back rank / near castling positions (in the current table: middlegame oriented).

### 4. Pawn promotion potential

There is an extra heuristic to reward pawns that are close to promoting.

- For **White pawns**:
	- Compute `rank = chess.square_rank(sq)` (0 = first rank, 7 = eighth rank).
	- Add `rank * 10` to the score for each pawn.
- For **Black pawns**:
	- Also compute the rank, but use distance from promotion:
	- Subtract `(7 − rank) * 10` from the score.

This means:

- Pawns on the 6th/7th ranks are quite valuable.
- The engine is more motivated to push advanced pawns and support their promotion.

The final evaluation combines everything:

- `total = material + pawn_table + pawn_promotion_bonus + knights + bishops + rooks + queens + kings`

Graphical User Interface (GUI)
------------------------------

The GUI is implemented in `gui.py` using Tkinter.

### Basics

- `ChessGUI` class wraps a `chess.Board` and handles drawing and user interaction.
- The board is drawn on a `tk.Canvas` as an 8×8 grid of squares.
- Pieces use Unicode symbols (♙♘♗♖♕♔ / ♟♞♝♜♛♚).

### Choosing a side and starting a game

- At the top, there are radio buttons to choose “White” or “Black” for the human.
- `New Game` resets the board and starts a fresh game.
- If the human chooses Black, the engine makes the first move as White.

### Making moves

- Click on one of your own pieces to **select** it.
	- The selected square is highlighted.
	- Legal destination squares for that piece are shown as small dots.
- Click on a destination square to attempt a move.
- The GUI creates the move by matching from–to squares against `board.legal_moves`.

### Pawn promotion in the GUI

When a pawn move reaches the last rank, `python-chess` exposes promotion moves as legal moves with a `promotion` attribute.

In the GUI:

- When multiple legal moves exist from the same `from_square` to the same `to_square` (i.e., different promotion pieces), it looks at those promotion moves.
- For now, promotions are **auto-queened**:
	- Prefer a promotion to a Queen.
	- If a Queen promotion doesn’t exist for some reason, fall back to the first promotion move.

This is simple but practical for a small engine GUI.

### Engine moves

- After the human moves, the GUI calls `_determine_best_move` with the current board and whose turn it is.
- The returned move is `board.push`ed, and the board is redrawn.
- The status bar shows whose turn it is and the last engine move (in UCI format).

Console Mode
------------

`engine.py` also contains a simple console mode under the `if __name__ == '__main__':` block.

- Asks whether to play as White or Black.
- Prints the board state as ASCII.
- On my turn, I enter moves in SAN (e.g., `e4`, `Nf3`, `Qxd5`).
- On the engine’s turn, it computes the best move and prints it.

Getting Started
---------------

### Requirements

- Python 3.x
- `python-chess`
- Tkinter (usually included with standard Python installations on most platforms)

### Installation

From the project root:

```bash
pip install -r requirements.txt
```

### Launching the GUI

From the project root:

```bash
python gui.py
```

### Running console mode

From the project root:

```bash
python engine.py
```

Notes / Possible Improvements
-----------------------------

- Add a dedicated endgame king table or phase-aware evaluation (different tables for middlegame vs endgame).
- Implement underpromotions (let the user choose the piece in the GUI instead of always queening).
- Add basic move ordering to help alpha–beta pruning be more effective.
- Add time control or iterative deepening instead of fixed search depth.

These details should give readers an overview of how the engine is structured and how the main search and evaluation logic works.
