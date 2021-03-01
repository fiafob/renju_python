# по всему коду при рисовании фигур можно увидеть + 1/2/3 пикселя - это не что-то особенное,
# просто ручная настройка чтобы все смотрелось более-менее приемлимо
import os
import random
import sys

import pygame

SIZE = WIDTH, HEIGHT = 900, 674
RC = 15  # renju_cells
COLOR = pygame.Color(200, 170, 0)  # тот оранжевый цвет
FONT = 'data/font/ARCADECLASSIC.TTF'  # pixel font
PNUM = 3  # количество разных моделей планет каждого цвета
PXS = 41  # допустимое значение фишки


#  открывает изображение
def load_image(name, colorkey=None):
    pygame.init()
    pygame.display.set_caption("Рэндзю")
    # без этой строки ничего не работает
    pygame.display.set_mode(SIZE)

    fullname = os.path.join("data", name)
    if not os.path.isfile(fullname):
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30
        self.chip_group = pygame.sprite.Group()

        # turn - определяет кто сейчас ходит. 1 - blue, 2 - red
        # p1 | p2 - player1 | player2 - сколько ходов сделал игрок
        self.turn = 1
        self.p1 = 0
        self.p2 = 0

        # rv - right version. Помогает при создании определенных вещей,
        # которые думают что находятся в поле 14х14
        self.rvx = self.get_size()[0] - self.cell_size
        self.rvy = self.get_size()[1] - self.cell_size

        # коэффицент затемнения
        self.shdwK = 30
        self.button_clicked = False

        # все действия выполняются после победы
        # переменная win блокирует нажатия на поле, чтобы не поставили фишки
        # не знаю как раньше обходилось без переменной screen
        # подебитель становится цветом (RED|BLUE)
        # индекс нужен, чтобы красиво отобразить победителя
        # stop нужен, чтобы прекратился счетчик
        # time нужен, чтобы текст исчез через 6 секунд
        self.win = False
        self.screen = None
        self.da_best_player = ""
        self.player_ind = 0
        self.stop = False
        self.time = 0

    def set_screen(self, screen):
        self.screen = screen

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

        self.rvx = self.get_size()[0] - self.cell_size
        self.rvy = self.get_size()[1] - self.cell_size

    def render(self, screen):
        # k - коэффицент толщины (рамки, фигур)
        k = 3

        self.help_rect(screen)
        self.nums_letts(screen)
        self.hud(screen)

        # само поле
        surf = pygame.Surface(SIZE, pygame.SRCALPHA)
        # cx, cy - count подсчитвыает текущее расположение ряда/колонны
        cy = self.top
        for row in self.board:
            cx = self.left
            for _ in row:
                for shadow_k in range(1, -1, -1):
                    color = pygame.Color(200, 170, 0)
                    hsv = color.hsva
                    color.hsva = (int(hsv[0]), int(hsv[1]),
                                  int(hsv[2] - 30 * shadow_k), int(hsv[3]))
                    # vertical line
                    pygame.draw.line(surf, color, (cx + k * shadow_k, self.top + k * shadow_k),
                                     (cx + k * shadow_k, self.rvy + self.top), width=k)
                    # horizontal line
                    pygame.draw.line(surf, color, (self.left, cy + shadow_k * k),
                                     (self.rvx + self.left, cy + k * shadow_k), width=k)

                cx += self.cell_size
            cy += self.cell_size
        # отображает 4 точки
        for k in range(1, 9, 7):
            pygame.draw.circle(surf, COLOR, (3 * self.cell_size + self.left + 1,
                                             (3 + k) * self.cell_size + self.top + 1), 8)
            pygame.draw.circle(surf, COLOR,
                               (self.get_size()[0] + self.left - self.cell_size * 4 + 1,
                                (3 + k) * self.cell_size + self.top + 1), 8)
        screen.blit(surf, (0, 0))
        self.chip_group.draw(screen)

        # отображается при победе кого-либо

        word = self.da_best_player + "  WINS"
        if self.player_ind > len(word):
            self.player_ind = len(word)
            self.stop = True
        if self.win:
            if self.player_ind > 0:
                font = pygame.font.Font(FONT, 3 * self.cell_size)
                text = font.render(word[:self.player_ind], True,
                                   pygame.Color(self.da_best_player))
                self.screen.blit(text, (WIDTH - (9 + self.player_ind) * self.cell_size,
                                        HEIGHT // 2.5))

    # Полупрозрачный квадрат, будет работать до 3 хода, помогает понять, где ходить
    def help_rect(self, screen):
        # создаю отдельную поверхность, где рисую поле
        surf = pygame.surface.Surface(SIZE, pygame.SRCALPHA)
        width, height = self.get_size()
        color = pygame.Color(200, 170, 0, 50)
        # p1 + p2 - общее количество ходов
        if self.p1 + self.p2 == 0:
            pygame.draw.rect(surf, color, ((((width - 2 * self.cell_size) // 2) + self.left + 2,
                                            ((height - 2 * self.cell_size) // 2) + self.top + 2),
                                           (self.cell_size, self.cell_size)))
        elif self.p1 + self.p2 == 1:
            pygame.draw.rect(surf, color, ((((width - 2 * self.cell_size) // 2) + self.left + 2,
                                            ((height - 4 * self.cell_size) // 2) + self.top + 2),
                                           (2 * self.cell_size, self.cell_size)))
        elif self.p1 + self.p2 == 2:
            pygame.draw.rect(surf, color, ((((width - 6 * self.cell_size) // 2) + self.left + 2,
                                            ((height - 6 * self.cell_size) // 2) + self.top + 2),
                                           (5 * self.cell_size, 5 * self.cell_size)))
        screen.blit(surf, (0, 0))

    # Отображает цифры и буквы
    def nums_letts(self, screen):
        font = pygame.font.Font(FONT, 2 * RC)
        for number in range(1, RC + 1):
            text = font.render(str(number), True, COLOR)
            screen.blit(text, (2 * self.left + self.rvx,
                               0.5 * self.top + (number - 1) * self.cell_size))

        letters = "ABCDEFGHIJKLMNO"
        for n in range(RC):
            text = font.render(letters[n], True, COLOR)
            screen.blit(text, (self.left // 1.5 + n * self.cell_size,
                               2 * self.top + self.rvy))

    def hud(self, screen):
        # показывает кто ходит в верхнем правом углу
        if not self.win:
            if self.turn == 2:
                txt_clr = pygame.Color(150, 0, 0)
                font = pygame.font.Font(FONT, int(2.5 * RC))
                text = font.render("RED  TURN", True, txt_clr)
                screen.blit(text, (self.get_size()[0] + 1.3 * self.cell_size,
                                   self.top))
            else:

                txt_clr = pygame.Color(0, 0, 170)
                font = pygame.font.Font(FONT, int(2.5 * RC))
                text = font.render("BLUE  TURN", True, txt_clr)
                screen.blit(text, (self.get_size()[0] + 1.3 * self.cell_size,
                                   self.top))

        self.button(screen)

    # кнопка перезагрузки доски
    def button(self, screen):
        btn_clr = pygame.Color(200, 170, 0)
        txt_clr = pygame.Color(240, 240, 240)
        font = pygame.font.Font(FONT, 2 * RC)
        for clr in [btn_clr, txt_clr]:
            hsv = clr.hsva
            clr.hsva = (int(hsv[0]), int(hsv[1]), int(hsv[2]) - self.shdwK, int(hsv[3]))
        x0, y0 = self.get_size()[0] + 2 * self.cell_size, HEIGHT - 2 * self.cell_size - self.top

        dy = 0
        if not self.button_clicked:
            btn_clr = (btn_clr[0] - 30, btn_clr[1] - 30, btn_clr[2])

            pygame.draw.rect(screen, (btn_clr[0] - 50, btn_clr[1] - 50, btn_clr[2]),
                             ((x0 - 1, y0 + self.cell_size // 2.8),
                              (int(3.5 * self.cell_size), int(1 * self.cell_size))),
                             border_radius=5)
        else:
            dy = 4
        pygame.draw.rect(screen, btn_clr, ((x0 - 1, y0 + self.cell_size // 3.8 + dy),
                                           (int(3.5 * self.cell_size), int(1 * self.cell_size))),
                         border_radius=5)
        text = font.render('RESTART', True, txt_clr)
        screen.blit(text, (x0 + self.cell_size // 2.4, y0 + self.cell_size // 2.5 + dy))

    # проверка, нажали ли на кнопку restart
    def button_check(self, mouse_pos):
        x0 = self.get_size()[0] + 2 * self.cell_size
        y0 = HEIGHT - 2 * self.cell_size - self.top
        if mouse_pos[0] in range(x0, x0 + int(3.5 * self.cell_size)) and \
                mouse_pos[1] in range(y0, y0 + int(1.5 * self.cell_size)):
            self.shdwK = 0
        else:
            self.shdwK = 30

    # если на кнопку действительно нажали
    def button_click(self, mouse_pos, action):
        x0 = self.get_size()[0] + 2 * self.cell_size
        y0 = HEIGHT - 2 * self.cell_size - self.top
        if mouse_pos[0] in range(x0, x0 + int(3.5 * self.cell_size)) and \
                mouse_pos[1] in range(y0, y0 + int(1.5 * self.cell_size)):
            if action == "down":
                self.button_clicked = True
            else:
                self.button_clicked = False
                self.update_desk()

    # обновляет данные при начале новой партии
    def update_desk(self):
        self.chip_group = pygame.sprite.Group()
        self.board = [[0] * self.width for _ in range(self.height)]
        self.p1, self.p2 = 0, 0
        self.turn = 1
        self.win = False
        self.stop = False
        self.player_ind = 0
        self.da_best_player = ""
        self.time = 0

    def get_cell(self, mouse_pos):
        # она определяет точку в поле 16x16, где одна клетка является переврестием
        if (mouse_pos[0] in range(0, int(self.width * self.cell_size))) and \
                (mouse_pos[1] in range(0, int(self.height * self.cell_size))):

            r = (mouse_pos[0]) // self.cell_size, (mouse_pos[1]) // self.cell_size
            print(r)

            return ((mouse_pos[0]) // self.cell_size,
                    (mouse_pos[1]) // self.cell_size)
        else:
            return None

    # обрабатывает что делать при нажатии
    def on_click(self, cell_coords):
        if cell_coords is not None:
            # здесь, 2 = k - 1 | (k - коэфицент толщины)
            nx, ny = cell_coords
            if self.board[ny][nx] == 0:
                # правила для первых ходов
                if (self.p1 + self.p2 == 0) and (cell_coords != (7, 7)):
                    return
                elif (self.p1 + self.p2 == 1) and (nx not in range(7, 9) or ny != 6):
                    return
                elif (self.p1 + self.p2 == 2) \
                        and (nx not in range(5, 10) or ny not in range(5, 10)):
                    return
                if self.turn == 2:
                    self.p1 += 1
                    chip = RedChip(self.chip_group)
                    chip.rect.x = nx * self.cell_size + 3
                    chip.rect.y = ny * self.cell_size + 2

                elif self.turn == 1:
                    self.p2 += 1
                    chip = BlueChip(self.chip_group)
                    chip.rect.x = nx * self.cell_size + 3
                    chip.rect.y = ny * self.cell_size + 2
                # если поле пустое, ему передается значение игрока, который ходит
                self.board[ny][nx] = self.turn

                self.turn = self.turn % 2 + 1

                # проверка, выиграл ли кто-нибудь
                self.win_check()

    # функция для основной программы можно сказать, чтобы сразу срабатывало
    def get_click(self, mouse_pos):

        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    # возвращает размер доски в пикселях
    def get_size(self):
        return self.cell_size * self.width, self.cell_size * self.height

    ########################################################################
    ########################################################################

    def winner(self, player, coords):
        print("winner", player)
        self.da_best_player = player
        self.win = True
        for coord in coords:
            coord = coord[1] * self.cell_size + self.left, \
                    coord[0] * self.cell_size + self.top
            self.chip_group.update(coord)

    def congrats_wnr(self):
        if not self.stop:
            self.player_ind += 1
        self.time += 1
        if self.time >= 5000 // 150:
            self.player_ind = 0

    ########################################################################

    def win_check(self):
        # horizontal/vertical check
        # т.к. доска 15х15, т.е. квадратная,
        # можно сразу проверить и вертикально и горизонтально
        for x in range(self.height):
            p1hcount, p2hcount = [], []
            p1vcount, p2vcount = [], []
            for y in range(self.width):
                if self.board[x][y] == 0:
                    p1hcount, p2hcount = [], []
                else:
                    num = self.board[x][y]
                    exec(f'p{num}hcount.append((x, y))')
                    exec(f'p{num % 2 + 1}hcount.clear()')

                if self.board[y][x] == 0:
                    p1vcount, p2vcount = [], []
                else:
                    num = self.board[y][x]
                    exec(f'p{num}vcount.append((y, x))')
                    exec(f'p{num % 2 + 1}vcount.clear()')

                if len(p1hcount) == 5 or len(p1vcount) == 5:
                    poses = max([p1hcount, p1vcount], key=lambda t: len(t))
                    self.winner("BLUE", poses)
                    return
                if len(p2hcount) == 5 or len(p2vcount) == 5:
                    poses = max([p2vcount, p2hcount], key=lambda t: len(t))
                    self.winner("RED", poses)
                    return

        # diag
        # проверка работает только на нижнюю половину доски,
        # поэтому нужно проверить и вторую часть
        for i in range(self.height):
            length = self.height - 1
            # счет по диагонали
            p1d1c, p2d1c = [], []
            p1d2c, p2d2c = [], []
            # счет на вторую половину
            hp1d1, hp2d1 = [], []
            hp1d2, hp2d2 = [], []

            for j in range(i + 1):
                if i < length:
                    if self.board[length - i + j][length - j] == 0:
                        hp1d1, hp2d1 = [], []
                    else:
                        num = self.board[length - i + j][length - j]
                        exec(f"hp{num}d1.append((length - i + j, length - j))")
                        exec(f"hp{num % 2 + 1}d1.clear()")

                    if self.board[j][length - i + j] == 0:
                        hp1d2, hp2d2 = [], []
                    else:
                        num = self.board[j][length - i + j]
                        exec(f'hp{num}d2.append((j, length - i + j))')
                        exec(f'hp{num % 2 + 1}d2.clear()')

                if self.board[i - j][j] == 0:
                    p1d1c, p2d1c = [], []
                else:
                    num = self.board[i - j][j]
                    exec(f"p{num}d1c.append((i - j, j))")
                    exec(f"p{num % 2 + 1}d1c.clear()")

                # вторая диагональ
                if self.board[length - j][i - j] == 0:
                    p1d2c, p2d2c = [], []
                else:
                    num = self.board[length - j][i - j]
                    exec(f"p{num}d2c.append((length - j, i - j))")
                    exec(f"p{num % 2 + 1}d2c.clear()")

                if (len(p1d1c) == 5 or len(p1d2c) == 5) or (len(hp1d1) == 5 or len(hp1d2) == 5):
                    poses = max([p1d1c, p1d2c, hp1d1, hp1d2], key=lambda t: len(t))
                    self.winner('BLUE', poses)
                    return
                elif (len(p2d1c) == 5 or len(p2d2c) == 5) \
                        or (len(hp2d1) == 5 or len(hp2d2) == 5):
                    poses = max([p2d1c, p2d2c, hp2d1, hp2d2], key=lambda t: len(t))
                    self.winner('RED', poses)
                    return


#########################################################################
#########################################################################
#########################################################################


class RedChip(pygame.sprite.Sprite):
    game_chip = load_image('img/red1.png')
    win_chip = load_image('img/red2.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = RedChip.game_chip
        self.rect = self.image.get_rect()

    def update(self, *args):
        if args and type(args[0]) == tuple and self.rect.collidepoint(args[0]):
            self.image = RedChip.win_chip


class BlueChip(pygame.sprite.Sprite):
    game_chip = load_image('img/blue1.png')
    win_chip = load_image('img/blue2.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = BlueChip.game_chip
        self.rect = self.image.get_rect()

    def update(self, *args):
        if args and type(args[0]) == tuple and self.rect.collidepoint(args[0]):
            self.image = BlueChip.win_chip


#########################################################################
#########################################################################
#########################################################################

# класс представляет задний фон из точек, который напоминает мерцающие звезды
class BackgroundBlink:
    def __init__(self, stars):
        self.stars = stars

        # случайное расположение звезд
        self.positions = [(random.randrange(WIDTH), random.randrange(HEIGHT))
                          for _ in range(stars)]

        # переменная, из-за которой звезды затухают
        self.darkness = 200

        # Определяет будет ли затухать звезда или появляться
        self.get_darker = False

    # создаю поверхность с звездами, потому что прозрачность можно менять у поверхностей
    def show_stars(self, screen):
        surf = pygame.Surface(SIZE, pygame.SRCALPHA)
        counter = 0
        k = 3
        for x, y in self.positions:
            color = pygame.Color(220, 255, 255, 200 - self.darkness)
            # Отображение разных звезд

            # простой плюсик
            if counter == 0:
                pygame.draw.line(surf, color, (x - k - 1, y), (x + k + 1, y), width=k)
                pygame.draw.line(surf, color, (x, y - k - 1), (x, y + k + 1), width=k)
            # перекрестие
            elif counter == 1:
                for kk in range(-k, k + 1, k):
                    pygame.draw.rect(surf, color, ((x + kk, y + kk), (k, k)), border_radius=1)
                    pygame.draw.rect(surf, color, ((x + kk, y - kk), (k, k)), border_radius=1)
                pygame.draw.rect(surf, color, ((x, y), (k, k)), border_radius=1)
            # ромб
            elif counter == 2:
                kk = 4
                for w in range(3):
                    kk = 4 if kk == 2 else 2
                    for q in range(kk):
                        z = 1 if q % 2 == 0 else -1
                        if q > 1:
                            pygame.draw.rect(surf, color, ((x + z * (2 - w) * k, y + z * w * k),
                                                           (k, k)), border_radius=1)
                        else:
                            pygame.draw.rect(surf, color, ((x + z * (2 - w) * k, y - z * w * k),
                                                           (k, k)), border_radius=1)

            counter = (counter + 1) % 3
        screen.blit(surf, (0, 0))

    # функция вызывается так, чтобы за 6 секунд звезда потухла
    def change_darkness(self):
        if self.darkness < 200 and self.get_darker:
            self.darkness += 1
        elif self.darkness > 0 and not self.get_darker:
            self.darkness -= 1
        elif self.darkness == 200:
            self.get_darker = False
        else:
            self.get_darker = True

    # функция обновляется каждые 12 секунд, меняя расположение звезд
    def update(self):
        self.darkness = 200
        self.positions = [(random.randrange(WIDTH), random.randrange(HEIGHT))
                          for _ in range(self.stars)]
