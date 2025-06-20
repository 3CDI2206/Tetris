import tkinter as tk
import random
import time
import subprocess
import sys

CELL = 30
COLS = 10
ROWS = 20
WALL = 1
COLORS = ["red", "green", "blue"]

SHAPES = [
    [[(0, 0), (1, 0), (0, 1), (1, 1)]],  # O
    [[(0, 0), (1, 0), (2, 0), (3, 0)], [(1, -1), (1, 0), (1, 1), (1, 2)]],  # I
    [[(0, 0), (0, 1), (0, 2), (1, 2)],
     [(0, 1), (1, 1), (2, 1), (0, 0)],
     [(0, 0), (1, 0), (1, 1), (1, 2)],
     [(0, 1), (1, 1), (2, 1), (2, 2)]],  # L
    [[(1, 0), (1, 1), (1, 2), (0, 2)],
     [(0, 0), (0, 1), (1, 1), (2, 1)],
     [(0, 0), (1, 0), (0, 1), (0, 2)],
     [(0, 1), (1, 1), (2, 1), (2, 0)]],  # J
    [[(0, 1), (1, 1), (2, 1), (1, 0)],
     [(1, 0), (1, 1), (1, 2), (0, 1)],
     [(0, 1), (1, 1), (2, 1), (1, 2)],
     [(1, 0), (1, 1), (1, 2), (2, 1)]],  # T
    [[(0, 0), (1, 0), (1, 1), (2, 1)],
     [(1, 0), (1, 1), (0, 1), (0, 2)]],  # S
    [[(0, 1), (1, 1), (1, 0), (2, 0)],
     [(0, 0), (0, 1), (1, 1), (1, 2)]]   # Z
]

class Tetris:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=(COLS + 8) * CELL, height=(ROWS + 2 * WALL) * CELL, bg="lightgray")
        self.canvas.pack()
        self.board = [[None for _ in range(COLS + 2 * WALL)] for _ in range(ROWS + 2 * WALL)]
        self.init_wall()
        self.previous_shapes = []
        self.current = self.create_block()
        self.queue = [self.create_block(), self.create_block()]
        self.flash_lines = []
        self.flash_phase = 0
        self.flashing = False
        self.base_speed = 500
        self.drop_speed = self.base_speed
        self.start_time = time.time()
        self.game_over_flag = False
        self.draw()
        self.drop()

        root.bind("<Left>", lambda e: self.move(-1))
        root.bind("<Right>", lambda e: self.move(1))
        root.bind("<r>", lambda e: self.rotate())
        root.bind("<R>", lambda e: self.rotate())
        root.bind("<Down>", lambda e: self.hard_drop())

    def init_wall(self):
        for y in range(ROWS + 2 * WALL):
            for x in range(COLS + 2 * WALL):
                if x < WALL or x >= COLS + WALL or y >= ROWS + WALL:
                    self.board[y][x] = "black"

    def create_block(self):
        while True:
            shape_index = random.randint(0, len(SHAPES) - 1)
            if self.previous_shapes.count(shape_index) < 2:
                break
        self.previous_shapes.append(shape_index)
        if len(self.previous_shapes) > 2:
            self.previous_shapes.pop(0)
        shape_variants = SHAPES[shape_index]
        return {
            "shapes": shape_variants,
            "rotation": 0,
            "color": random.choice(COLORS),
            "x": COLS // 2 + WALL - 1,
            "y": WALL
        }

    def get_coords(self):
        shape = self.current["shapes"][self.current["rotation"]]
        return [(self.current["x"] + dx, self.current["y"] + dy) for dx, dy in shape]

    def move(self, dx):
        if self.game_over_flag:
            return
        self.current["x"] += dx
        if not self.valid():
            self.current["x"] -= dx
        self.draw()

    def rotate(self):
        if self.game_over_flag:
            return
        old_rotation = self.current["rotation"]
        self.current["rotation"] = (self.current["rotation"] + 1) % len(self.current["shapes"])
        if not self.valid():
            self.current["rotation"] = old_rotation
        self.draw()

    def hard_drop(self):
        if self.game_over_flag or self.flashing:
            return
        while True:
            self.current["y"] += 1
            if not self.valid():
                self.current["y"] -= 1
                break
        self.lock()
        lines = self.check_lines()
        if lines:
            self.flash(lines)
        self.current = self.queue.pop(0)
        self.queue.append(self.create_block())
        if not self.valid():
            self.game_over()
            return
        self.draw()

    def valid(self):
        for x, y in self.get_coords():
            if self.board[y][x]:
                return False
        return True

    def lock(self):
        for x, y in self.get_coords():
            self.board[y][x] = self.current["color"]

    def check_lines(self):
        lines = []
        for y in range(WALL, ROWS + WALL):
            if all(self.board[y][x] for x in range(WALL, COLS + WALL)):
                lines.append(y)
        return lines

    def delete_lines(self, lines):
        for y in lines:
            for x in range(WALL, COLS + WALL):
                self.board[y][x] = None
        for line in sorted(lines):
            for y in range(line, WALL, -1):
                for x in range(WALL, COLS + WALL):
                    self.board[y][x] = self.board[y - 1][x]
            for x in range(WALL, COLS + WALL):
                self.board[WALL][x] = None

    def flash(self, lines):
        self.flash_lines = lines
        self.flashing = True
        self.flash_phase = 0
        self.flash_animation()

    def flash_animation(self):
        self.flash_phase += 1
        for y in self.flash_lines:
            for x in range(WALL, COLS + WALL):
                self.board[y][x] = "white" if self.flash_phase % 2 == 1 else "gray"
        self.draw()
        if self.flash_phase < 6:
            self.canvas.after(150, self.flash_animation)
        else:
            self.delete_lines(self.flash_lines)
            self.flashing = False
            self.flash_lines = []
            self.draw()

    def drop(self):
        if self.flashing or self.game_over_flag:
            self.canvas.after(100, self.drop)
            return

        elapsed = time.time() - self.start_time
        speed_up = int(elapsed // 30) * 50
        self.drop_speed = max(100, self.base_speed - speed_up)

        self.current["y"] += 1
        if not self.valid():
            self.current["y"] -= 1
            self.lock()
            lines = self.check_lines()
            if lines:
                self.flash(lines)
            self.current = self.queue.pop(0)
            self.queue.append(self.create_block())
            if not self.valid():
                self.game_over()
                return
        self.draw()
        self.canvas.after(self.drop_speed, self.drop)

    def game_over(self):
        self.game_over_flag = True
        self.canvas.create_text((COLS + WALL) * CELL // 2, (ROWS + WALL) * CELL // 2,
                                text="GAME OVER", fill="black", font=("Helvetica", 24, "bold"))
        self.root.after(3000, self.back_to_menu)

    def back_to_menu(self):
        self.root.destroy()
        subprocess.Popen([sys.executable, "main_menu.py"])

    def draw(self):
        self.canvas.delete("all")
        for y in range(ROWS + 2 * WALL):
            for x in range(COLS + 2 * WALL):
                color = self.board[y][x]
                if color:
                    self.draw_cell(x, y, color)
                else:
                    self.canvas.create_rectangle(x * CELL, y * CELL, (x + 1) * CELL, (y + 1) * CELL,
                                                 outline="gray", fill="white")
        for x, y in self.get_coords():
            self.draw_cell(x, y, self.current["color"])
        for i, block in enumerate(self.queue):
            shape = block["shapes"][0]
            for dx, dy in shape:
                self.draw_cell(COLS + WALL + 2 + dx, WALL + i * 4 + dy, block["color"])

    def draw_cell(self, x, y, color):
        self.canvas.create_rectangle(x * CELL, y * CELL, (x + 1) * CELL, (y + 1) * CELL,
                                     fill=color, outline="black")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Tetris")
    Tetris(root)
    root.mainloop()
    