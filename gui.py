import tkinter as tk
from tkinter import messagebox

import chess

from engine import _determine_best_move


def piece_to_unicode(piece: chess.Piece | None) -> str:
    if piece is None:
        return ""
    mapping_white = {
        chess.PAWN: "♙",
        chess.KNIGHT: "♘",
        chess.BISHOP: "♗",
        chess.ROOK: "♖",
        chess.QUEEN: "♕",
        chess.KING: "♔",
    }
    mapping_black = {
        chess.PAWN: "♟",
        chess.KNIGHT: "♞",
        chess.BISHOP: "♝",
        chess.ROOK: "♜",
        chess.QUEEN: "♛",
        chess.KING: "♚",
    }
    if piece.color == chess.WHITE:
        return mapping_white.get(piece.piece_type, "")
    return mapping_black.get(piece.piece_type, "")


class ChessGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Simple Chess Engine GUI")

        self.board = chess.Board()
        self.square_size = 64
        self.canvas_size = self.square_size * 8

        # Game state
        self.human_is_white = True
        self.selected_square: chess.Square | None = None
        self.highlight_moves: list[chess.Move] = []

        # UI elements
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=5)

        tk.Label(top_frame, text="Play as:").pack(side=tk.LEFT)
        self.color_var = tk.StringVar(value="white")
        tk.Radiobutton(
            top_frame,
            text="White",
            variable=self.color_var,
            value="white",
            command=self.on_color_change,
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            top_frame,
            text="Black",
            variable=self.color_var,
            value="black",
            command=self.on_color_change,
        ).pack(side=tk.LEFT)

        self.new_game_button = tk.Button(top_frame, text="New Game", command=self.new_game)
        self.new_game_button.pack(side=tk.LEFT, padx=10)

        self.status_label = tk.Label(self.root, text="Welcome to Simple Chess Engine", anchor="w")
        self.status_label.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.new_game()

    def on_color_change(self) -> None:
        # Only take effect on next new game; current game not flipped mid-play
        self.human_is_white = self.color_var.get() == "white"

    def new_game(self) -> None:
        self.board.reset()
        self.selected_square = None
        self.highlight_moves = []
        self.human_is_white = self.color_var.get() == "white"
        self.update_status()
        self.draw_board()

        # If human chose black, let engine (white) move first
        if not self.human_is_white:
            self.root.after(100, self.engine_move)

    # --- Board rendering helpers ---
    def draw_board(self) -> None:
        self.canvas.delete("all")

        colors = ("#F0D9B5", "#B58863")  # light, dark
        for rank in range(8):
            for file in range(8):
                x1 = file * self.square_size
                y1 = (7 - rank) * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                color_index = (file + rank) % 2
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=colors[color_index], outline="black")

                square = chess.square(file, rank)

                # Highlight selected square
                if self.selected_square == square:
                    self.canvas.create_rectangle(
                        x1,
                        y1,
                        x2,
                        y2,
                        outline="yellow",
                        width=3,
                    )

                # Highlight possible destination squares
                if any(move.to_square == square for move in self.highlight_moves):
                    self.canvas.create_oval(
                        x1 + self.square_size / 3,
                        y1 + self.square_size / 3,
                        x2 - self.square_size / 3,
                        y2 - self.square_size / 3,
                        outline="",
                        fill="gray25",
                    )

                piece = self.board.piece_at(square)
                if piece is not None:
                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text=piece_to_unicode(piece),
                        font=("Helvetica", int(self.square_size * 0.6)),
                    )

    def pixel_to_square(self, x: int, y: int) -> chess.Square | None:
        if not (0 <= x < self.canvas_size and 0 <= y < self.canvas_size):
            return None
        file = x // self.square_size
        rank_from_top = y // self.square_size
        rank = 7 - rank_from_top
        return chess.square(file, rank)

    # --- Game logic ---
    def on_canvas_click(self, event) -> None:
        if self.board.is_game_over():
            return

        human_color = chess.WHITE if self.human_is_white else chess.BLACK
        if self.board.turn != human_color:
            # Not human's turn
            return

        square = self.pixel_to_square(event.x, event.y)
        if square is None:
            return

        piece = self.board.piece_at(square)

        if self.selected_square is None:
            # First click: select a piece of the human's color
            if piece is None or piece.color != human_color:
                return
            self.selected_square = square
            self.highlight_moves = [m for m in self.board.legal_moves if m.from_square == square]
        else:
            # Second click: attempt move (including promotions)
            candidate_moves = [
                m for m in self.board.legal_moves
                if m.from_square == self.selected_square and m.to_square == square
            ]

            if candidate_moves:
                # If there are promotion choices, auto-queen by default
                move = None
                promotion_moves = [m for m in candidate_moves if m.promotion is not None]
                if promotion_moves:
                    # Prefer queen promotion if available
                    queen_promotions = [m for m in promotion_moves if m.promotion == chess.QUEEN]
                    move = queen_promotions[0] if queen_promotions else promotion_moves[0]
                else:
                    move = candidate_moves[0]

                self.board.push(move)
                self.selected_square = None
                self.highlight_moves = []
                self.draw_board()
                self.update_status()

                if self.board.is_game_over():
                    self.show_game_over()
                else:
                    # Engine's turn
                    self.root.after(100, self.engine_move)
                return
            else:
                # If clicked own piece again, change selection
                if piece is not None and piece.color == human_color:
                    self.selected_square = square
                    self.highlight_moves = [m for m in self.board.legal_moves if m.from_square == square]
                else:
                    # Invalid destination; clear selection
                    self.selected_square = None
                    self.highlight_moves = []

        self.draw_board()

    def engine_move(self) -> None:
        if self.board.is_game_over():
            return

        is_white_turn = self.board.turn == chess.WHITE

        move = _determine_best_move(self.board, is_white_turn)
        if move is None:
            # No legal moves
            self.show_game_over()
            return

        self.board.push(move)
        self.draw_board()
        self.update_status(engine_move=move)

        if self.board.is_game_over():
            self.show_game_over()

    def update_status(self, engine_move: chess.Move | None = None) -> None:
        if self.board.is_game_over():
            result_text = "Game over: " + self.board.result(claim_draw=True)
            self.status_label.config(text=result_text)
            return

        turn_color = "White" if self.board.turn == chess.WHITE else "Black"
        parts = [f"Turn: {turn_color}"]
        if engine_move is not None:
            parts.append(f"Engine played: {engine_move.uci()}")
        self.status_label.config(text=" | ".join(parts))

    def show_game_over(self) -> None:
        outcome = self.board.outcome(claim_draw=True)
        if outcome is None:
            text = "Game over"
        else:
            if outcome.winner is None:
                text = "Draw"
            elif outcome.winner == chess.WHITE:
                text = "White wins"
            else:
                text = "Black wins"
        messagebox.showinfo("Game Over", text)
        self.update_status()


def main() -> None:
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
