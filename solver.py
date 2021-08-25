class Solver:
    def __init__(self, grid):
        self.grid = grid
        self.solved = False

    def check(self, x, y, value):
        for i in range(9):
            if self.grid[x][i] == value or self.grid[i][y] == value:
                return False
        x0, y0 = (x // 3) * 3, (y // 3) * 3
        for i in range(3):  # Square
            for j in range(3):
                if self.grid[x0 + i][y0 + j] == value:
                    return False
        return True

    def fill(self, x, y, value):
        self.grid[x][y] = value
