import pygame
import pygame_menu
import requests
from time import sleep
from solver import Solver

WHITE = (255, 255, 255)
SELECTED_COLOR = (220, 220, 220)
GRID_COLOR = (90, 111, 140)
FONT_COLOR = GRID_COLOR


class Square(pygame.Rect):
    def __init__(self, x, y, w, h, surface, fsize=72):
        super().__init__(x, y, w, h)
        self.surface = surface
        self.fontsize = fsize
        self.value = None
        self.prefilled = False
        self.eraser = False
        self.filler_enabled = False

    def change_color(self, col):
        self.display_value(col)

    def change_value(self, val):
        if val and val == 10:
            val = 'X'
            self.eraser = True
            self.filler_enabled = True
        self.value = val
        self.display_value()

    def display_value(self, col=FONT_COLOR):
        font = pygame.font.Font(None, self.fontsize)
        text = font.render(str(self.value) if self.value else '', True, col)
        text_rect = text.get_rect()
        text_rect.center = self.center
        self.surface.blit(text, text_rect)


class Sudoku:
    def __init__(self, FPS=60):
        self.FPS = FPS
        self.level = 1
        self.selected = tuple()
        self.screenSize = (580, 650)
        self.solved = False
        self.screen = pygame.display.set_mode(self.screenSize)
        self.grid = list()
        self.filler = list()
        pygame.init()
        pygame.display.set_caption('Sudoku')
        self.setup_menu()

    def setup_menu(self):
        self.menu = pygame_menu.Menu(
            title='Sudoku', height=600, width=530, theme=pygame_menu.themes.THEME_BLUE)
        self.menu.add.label('Welcome!')
        self.menu.add.selector('Difficulty', [(
            'Easy', 1), ('Medium', 2), ('Hard', 3)], onchange=self.set_difficulty)
        self.menu.add.button('Start', self.run)
        self.menu.add.button('Quit', pygame_menu.events.EXIT)

    def set_difficulty(self, value, difficulty):
        self.level = difficulty

    def start(self):
        self.menu.mainloop(self.screen)

    def newgame(self):
        try:
            response = requests.get(
                'https://www.cs.utep.edu/cheon/ws/sudoku/new/', {'size': '9', 'level': str(self.level)}, verify=False)
        except Exception as e:
            print(f'Error: {e}')
            quit(1)
        data = response.json()
        if data['response']:
            for square in data['squares']:
                self.grid[square['x']][square['y']
                                       ].change_value(square['value'])
                self.grid[square['x']][square['y']].prefilled = True

    def drawBoard(self):
        x, y, w, h = 20, 20, 60, 60
        f_x, f_y = x * 5, y * 2 + h * 9
        for row in range(10):
            f_sq = Square(f_x + row * 40, f_y, 40, 40, self.screen, 40)
            pygame.draw.rect(self.screen, WHITE, f_sq)
            f_sq.change_value(row + 1)
            f_sq.change_color(SELECTED_COLOR if row != 9 else FONT_COLOR)
            self.filler.append(f_sq)
        for row in range(9):
            cols = list()
            for col in range(9):
                square = Square(x + col * w, y + row * h, w, h, self.screen)
                cols.append(square)
                pygame.draw.rect(self.screen, GRID_COLOR, square, 1)
            self.grid.append(cols)

    def drawLines(self):
        x, y, w, h = 20, 20, 180, 180
        for row in range(3):
            for col in range(3):
                pygame.draw.rect(self.screen, GRID_COLOR, pygame.Rect(
                    x + col * w, y + row * h, w, h), 3)

    def update_filler(self, x, y):
        for filler in self.filler[:-1]:
            if self.solver.check(x, y, filler.value):
                filler.change_color(GRID_COLOR)
                filler.filler_enabled = True
            else:
                filler.change_color(SELECTED_COLOR)
                filler.filler_enabled = False

    def run(self):
        self.screen.fill(WHITE)
        self.drawBoard()
        self.newgame()
        self.solver = Solver(
            [[col.value if col.value else 0 for col in row] for row in self.grid])
        prev = None
        loop = True
        while loop:
            self.drawLines()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    for x, row in enumerate(self.grid):
                        for y, sq in enumerate(row):
                            if sq.collidepoint(pos) and not sq.prefilled:
                                self.selected = (x, y)
                                if prev:
                                    pygame.draw.rect(self.screen, WHITE, prev)
                                    pygame.draw.rect(
                                        self.screen, GRID_COLOR, prev, 1)
                                    prev.display_value(col=(0, 0, 0))
                                prev = sq
                                pygame.draw.rect(
                                    self.screen, SELECTED_COLOR, sq)
                                pygame.draw.rect(
                                    self.screen, GRID_COLOR, sq, 1)
                                sq.display_value(col=(0, 0, 0))
                                self.update_filler(x, y)
                    for filler in self.filler:
                        if filler.collidepoint(pos) and self.selected and filler.filler_enabled:
                            sel = self.grid[self.selected[0]][self.selected[1]]
                            pygame.draw.rect(self.screen, SELECTED_COLOR, sel)
                            pygame.draw.rect(self.screen, GRID_COLOR, sel, 1)
                            if filler.eraser:
                                sel.change_value(None)
                                self.solver.fill(
                                    self.selected[0], self.selected[1], 0)
                                sel.change_color((0, 0, 0))
                            else:
                                sel.change_value(filler.value)
                                self.solver.fill(
                                    self.selected[0], self.selected[1], filler.value)
                                sel.change_color((0, 0, 0))
                            self.update_filler(
                                self.selected[0], self.selected[1])
            pygame.display.flip()
            sleep(1/self.FPS)


if __name__ == '__main__':
    game = Sudoku()
    game.start()
