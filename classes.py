import random

import pygame

SIZE = WIDTH, HEIGHT = 1000, 780
RC = 15  # renju_cells
COLOR = pygame.Color(200, 170, 0)


# Очень сырой вариант : крестики-нолики вместо фишек // поле накладывается одно поверх другого
# какие-то границы есть стремные.
#
# Стоит добавить функцию, которая возвращает количество пикселей, которое занимает поле
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

        self.turn = 1

        # rv - right version
        self.rvx, self.rvy = self.get_size()[0] - self.cell_size, self.get_size()[1] - self.cell_size

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

        # rv - right version
        self.rvx, self.rvy = self.get_size()[0] - self.cell_size, self.get_size()[1] - self.cell_size

    def render(self, screen):
        # k - коэффицент толщины рамки
        k = 3

        size = width, height = self.get_size()

        # Полупрозрачный квадрат, будет работать до 3 хода, помогает понять, где ходить
        color = pygame.Color(200, 170, 0)
        hsv = color.hsva
        color.hsva = (int(hsv[0]), int(hsv[1]), int(hsv[2]) - 60, int(hsv[3]))
        pygame.draw.rect(screen, color, (((width // 2) - 3 * self.cell_size + self.left,
                                          (height // 2) - 3 * self.cell_size + self.top),
                                         (self.cell_size * 5, self.cell_size * 5)))

        # само поле
        # cx, cy - count подсчитвыает текущее расположение ряда/колонны
        cy = self.top
        for row in self.board:
            cx = self.left
            for elem in row:
                for shadow_k in range(1, -1, -1):
                    color = pygame.Color(200, 170, 0)
                    hsv = color.hsva
                    color.hsva = (int(hsv[0]), int(hsv[1]), int(hsv[2] - 30 * shadow_k), int(hsv[3]))
                    # vertical line
                    pygame.draw.line(screen, color, (cx + k * shadow_k, self.top + k * shadow_k),
                                     (cx + k * shadow_k, self.rvy + self.top), width=k)
                    # horizontal line
                    pygame.draw.line(screen, color, (self.left, cy + shadow_k * k),
                                     (self.rvx + self.left, cy + k * shadow_k), width=k)

                # На это пока забить можно, это фигура хода в общем
                if elem == 1:
                    pygame.draw.line(screen, (0, 0, 255),
                                     (cx + 3 * k, cy + 3 * k),
                                     (cx + self.cell_size - 3 * k, cy + self.cell_size - 3 * k), width=k)
                    pygame.draw.line(screen, (0, 0, 255),
                                     (cx + self.cell_size - 3 * k, cy + 3 * k),
                                     (cx + 3 * k, cy + self.cell_size - 3 * k), width=k)
                elif elem == 2:
                    pygame.draw.circle(screen, (255, 0, 0),
                                       (cx + 0.5 * self.cell_size + k, cy + 0.5 * self.cell_size + k),
                                       self.cell_size // 2 - 2 * k, width=k)

                cx += self.cell_size
            cy += self.cell_size

        # 4 точки, пока не знаю для чего они
        for k in range(1, 9, 7):
            pygame.draw.circle(screen, COLOR, (3 * self.cell_size + self.left + 1,
                                               (3 + k) * self.cell_size + self.top + 1), 8)
            pygame.draw.circle(screen, COLOR, (self.get_size()[0] + self.left - self.cell_size * 4 + 1,
                                               (3 + k) * self.cell_size + self.top + 1), 8)

    # Возможно это в итоге не пригодится, но сейчас это нужно чтобы понимать как работает игра
    # Отображает цифры и буквы
    def nums_letts(self, screen):
        font = pygame.font.Font(None, 2 * RC)
        for number in range(1, RC + 1):
            text = font.render(str(number), True, COLOR)
            screen.blit(text, (2 * self.left + self.rvx,
                               0.5 * self.top + (number - 1) * self.cell_size))

        letters = "ABCDEFGHIJKLMNO"
        for n in range(RC):
            text = font.render(letters[n], True, COLOR)
            screen.blit(text, (self.left // 2 + n * self.cell_size,
                               2 * self.top + self.rvy))
#############################################################################################
#############################################################################################

    # тут поменять надо чуть-чуть, чтобы "клеткой" называлось перекрестие, а не пустое пространство
    def get_cell(self, mouse_pos):
        if (mouse_pos[0] in range(self.left, self.left + self.width * self.cell_size)) and \
                (mouse_pos[1] in range(self.top, self.top + self.height * self.cell_size)):
            return ((mouse_pos[0] - self.left) // self.cell_size,
                    (mouse_pos[1] - self.top) // self.cell_size)
        else:
            return None

    # обрабатывает что делать при нажатии
    def on_click(self, cell_coords):
        if cell_coords is not None:
            if self.board[cell_coords[1]][cell_coords[0]] == 0:
                self.board[cell_coords[1]][cell_coords[0]] = self.turn
                self.turn = self.turn % 2 + 1

        print(cell_coords)

    # функция для основной программы можно сказать, чтобы сразу срабатывало
    def get_click(self, mouse_pos):

        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

########################################################################

    # возвращает размер доски
    def get_size(self):
        return self.cell_size * self.width, self.cell_size * self.height


#########################################################################
#########################################################################
#########################################################################

# класс представляет задний фон из точек, который напоминает мерцающие звезды
class BackgroundBlink:
    def __init__(self, stars):
        self.stars = stars

        # случайное расположение звезд
        self.positions = [(random.randrange(WIDTH), random.randrange(HEIGHT)) for _ in range(stars)]

        # переменная, из-за которой звезды затухают
        self.darkness = 0

    # создаю поверхность с звездами, потому что прозрачность можно менять у поверхностей
    def show_stars(self, screen):
        surf = pygame.Surface(SIZE, pygame.SRCALPHA)
        counter = 0
        k = 3
        for x, y in self.positions:
            color = pygame.Color(255, 255, 255, 200 - self.darkness)
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
        if self.darkness < 200:
            self.darkness += 1

    # функция обновляется каждые 6 секунд, меняя расположение звезд
    def update(self):
        self.darkness = 0
        self.positions = [(random.randrange(WIDTH), random.randrange(HEIGHT)) for _ in range(self.stars)]
