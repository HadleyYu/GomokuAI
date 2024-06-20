import tkinter as tk
from tkinter import messagebox
import random

class Gomoku:
    def __init__(self, master):
        self.master = master
        self.master.title('Gomoku')
        self.board_size = 15
        self.cell_size = 40
        self.canvas = tk.Canvas(self.master, width=self.board_size * self.cell_size, height=self.board_size * self.cell_size, bg='tan')
        self.canvas.pack()
        self.choose_color()

    def choose_color(self):
        color_choice = messagebox.askyesno("Choose Color", "Would you like to play as black?")
        self.player_color = "black" if color_choice else "white"
        self.ai_color = "white" if self.player_color == "black" else "black"
        self.current_color = "black"  # Black always starts in Gomoku
        self.init_game()

    def init_game(self):
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.canvas.bind("<Button-1>", self.place_stone)
        self.draw_board()
        if self.ai_color == "black":
            self.ai_move()

    def draw_board(self):
        for i in range(self.board_size):
            self.canvas.create_line(self.cell_size // 2, (i + 0.5) * self.cell_size, self.board_size * self.cell_size - self.cell_size // 2, (i + 0.5) * self.cell_size)
            self.canvas.create_line((i + 0.5) * self.cell_size, self.cell_size // 2, (i + 0.5) * self.cell_size, self.board_size * self.cell_size - self.cell_size // 2)

    def place_stone(self, event):
        if self.current_color != self.player_color:
            return  # Ignore clicks when it's AI's turn
        x, y = event.x // self.cell_size, event.y // self.cell_size
        if self.board[y][x] is None:
            self.board[y][x] = self.player_color
            self.draw_stone(x, y, self.player_color)
            self.canvas.after(100, lambda: self.check_game_end(x, y))

    def draw_stone(self, x, y, color):
        x_center = (x + 0.5) * self.cell_size
        y_center = (y + 0.5) * self.cell_size
        radius = self.cell_size // 2 - 4
        if color == "black":
            self.canvas.create_oval(x_center - radius, y_center - radius, x_center + radius, y_center + radius, fill='black')
        else:
            self.canvas.create_oval(x_center - radius, y_center - radius, x_center + radius, y_center + radius, outline='white', width=2)

    def check_game_end(self, x, y):
        if self.check_winner(x, y):
            self.display_winner()
        else:
            self.current_color = self.ai_color if self.current_color == self.player_color else self.player_color
            if self.current_color == self.ai_color:
                self.master.after(500, self.ai_move)

    def check_winner(self, x, y):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dx, dy in directions:
            count = 1
            for d in [1, -1]:
                step = 1
                while True:
                    nx, ny = x + step * dx * d, y + step * dy * d
                    if 0 <= nx < self.board_size and 0 <= ny < self.board_size and self.board[ny][nx] == self.current_color:
                        count += 1
                    else:
                        break
                    step += 1
            if count >= 5:
                return True
        return False

    def display_winner(self):
        winner_message = f'{self.current_color.capitalize()} wins!'
        messagebox.showinfo("Game Over", winner_message)
        self.ask_restart()

    def ask_restart(self):
        if messagebox.askyesno("Play Again?", "Would you like to play again?"):
            self.canvas.delete("all")
            self.choose_color()
        else:
            self.master.destroy()

    def minimax(self, depth, maximizing_player, alpha, beta):
        # Base case: depth is 0 or game has ended
        if depth == 0 or self.check_game_ended():
            return self.evaluate_board(), None
        
        if maximizing_player:
            max_eval = float('-inf')
            best_move = None
            for x in range(self.board_size):
                for y in range(self.board_size):
                    if self.board[y][x] is None:
                        # Make the move
                        self.board[y][x] = self.ai_color
                        # Recurse with minimax for the minimizing player
                        eval = self.minimax(depth - 1, False, alpha, beta)[0]
                        # Undo the move
                        self.board[y][x] = None
                        if eval > max_eval:
                            max_eval = eval
                            best_move = (x, y)
                        alpha = max(alpha, eval)
                        # Alpha-Beta pruning
                        if beta <= alpha:
                            break  # Prune the branch
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for x in range(self.board_size):
                for y in range(self.board_size):
                    if self.board[y][x] is None:
                        # Make the move
                        self.board[y][x] = self.player_color
                        # Recurse with minimax for the maximizing player
                        eval = self.minimax(depth - 1, True, alpha, beta)[0]
                        # Undo the move
                        self.board[y][x] = None
                        if eval < min_eval:
                            min_eval = eval
                            best_move = (x, y)
                        beta = min(beta, eval)
                        # Alpha-Beta pruning
                        if beta <= alpha:
                            break  # Prune the branch
            return min_eval, best_move


    def evaluate_board(self):
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[y][x] == self.ai_color:
                    score += self.evaluate_position(x, y, self.ai_color, directions)
                elif self.board[y][x] == self.player_color:
                    score -= self.evaluate_position(x, y, self.player_color, directions)
        return score

    def evaluate_position(self, x, y, color, directions):
        score = 0
        for dx, dy in directions:
            line_length = 1
            open_ends = 0

            # Forward direction
            steps = 1
            while steps <= 5:
                nx, ny = x + dx * steps, y + dy * steps
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                    if self.board[ny][nx] == color:
                        line_length += 1
                    elif self.board[ny][nx] is None:
                        open_ends += 1
                        break
                    else:
                        break
                else:
                    break
                steps += 1

            # Backward direction
            steps = 1
            while steps <= 5:
                nx, ny = x - dx * steps, y - dy * steps
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                    if self.board[ny][nx] == color:
                        line_length += 1
                    elif self.board[ny][nx] is None:
                        open_ends += 1
                        break
                    else:
                        break
                else:
                    break
                steps += 1

            # Score based on patterns
            if line_length >= 5:
                score += 10000000  # Winning condition
            elif line_length == 4:
                if open_ends == 2:
                    score += 5000  # Open four: can win in two ways
                elif open_ends == 1:
                    score += 500  # Closed four: can win in one move
            elif line_length == 3:
                if open_ends == 2:
                    score += 1000  # Open three: potential to create an open four
                elif open_ends == 1:
                    score += 100  # Closed three
            elif line_length == 2:
                if open_ends == 2:
                    score += 100  # Open two: potential to create an open three
                elif open_ends == 1:
                    score += 10  # Closed two
                    
        return score

    def check_game_ended(self):
        # Simplified check; should implement full win/lose check for game end.
        return any(self.check_winner(x, y) for x in range(self.board_size) for y in range(self.board_size) if self.board[y][x] is not None)

    def is_board_empty(self):
        return all(self.board[y][x] is None for x in range(self.board_size) for y in range(self.board_size))

    def place_near(self, x, y):
        # Attempt to place near the given position
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size and self.board[ny][nx] is None:
                    self.board[ny][nx] = self.ai_color
                    self.draw_stone(nx, ny, self.ai_color)
                    self.canvas.after(100, lambda: self.check_game_end(nx, ny))
                    return

    def is_first_ai_move(self):
        return sum(1 for x in range(self.board_size) for y in range(self.board_size) if self.board[y][x] == self.ai_color) == 0

    def find_initial_black_move(self):
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[y][x] == "black":
                    return x, y
        return self.board_size // 2, self.board_size // 2  # Default to center if no move found
        
#    def ai_move(self):
#        if self.current_color != self.ai_color:
#            return
#        empty_positions = [(x, y) for x in range(self.board_size) for y in range(self.board_size) if self.board[y][x] is None]
#        if empty_positions:
#            x, y = random.choice(empty_positions)
#            self.board[y][x] = self.ai_color
#            self.draw_stone(x, y, self.ai_color)
#            self.canvas.after(100, lambda: self.check_game_end(x, y))
        
    def ai_move(self):
        if self.current_color != self.ai_color:
            return

        # Check if it's the very first move for the AI
        if self.is_first_ai_move():
            if self.ai_color == "black":
                # Place on the center of the board if AI is black and it's the first move of the game
                x, y = self.board_size // 2, self.board_size // 2
                self.board[y][x] = self.ai_color
                self.draw_stone(x, y, self.ai_color)
                self.canvas.after(100, lambda: self.check_game_end(x, y))
                return
            else:
                # If AI is white, find the black move and place around it
                x, y = self.find_initial_black_move()
                self.place_near(x, y)
                return

        # Use minimax to find the best move
        _, move = self.minimax(2, True, float('-inf'), float('inf'))  # Depth set to 2 for simplicity
        if move:
            x, y = move
            self.board[y][x] = self.ai_color
            self.draw_stone(x, y, self.ai_color)
            self.canvas.after(100, lambda: self.check_game_end(x, y))
        else:
            # Fallback if no move found: place the first available spot
            for x in range(self.board_size):
                for y in range(self.board_size):
                    if self.board[y][x] is None:
                        self.board[y][x] = self.ai_color
                        self.draw_stone(x, y, self.ai_color)
                        self.canvas.after(100, lambda: self.check_game_end(x, y))
                        return

    def is_first_ai_move(self):
        return sum(1 for x in range(self.board_size) for y in range(self.board_size) if self.board[y][x] == self.ai_color) == 0

    def find_initial_black_move(self):
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[y][x] == "black":
                    return x, y
        return self.board_size // 2, self.board_size // 2  # Default to center if no move found

    def place_near(self, x, y):
        # Attempt to place near the given position
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size and self.board[ny][nx] is None:
                    self.board[ny][nx] = self.ai_color
                    self.draw_stone(nx, ny, self.ai_color)
                    self.canvas.after(100, lambda: self.check_game_end(nx, ny))
                    return

if __name__ == "__main__":
    root = tk.Tk()
    game = Gomoku(root)
    root.mainloop()
